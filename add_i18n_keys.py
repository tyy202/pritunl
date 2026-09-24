#!/usr/bin/env python3
"""
Script to add missing i18n keys to www/i18n/index.js
and update templates/views to use i18n.t()
"""
import re, os, json

# Define all missing translation keys
TRANSLATIONS = {
    # --- Navigation ---
    'nav.hosts': {'en': 'Hosts', 'zh': '主机'},
    'nav.admins': {'en': 'Administrators', 'zh': '管理员'},
    'nav.links': {'en': 'Links', 'zh': '链接'},
    'nav.logs': {'en': 'Logs', 'zh': '日志'},
    'nav.settings': {'en': 'Settings', 'zh': '设置'},
    'nav.lang': {'en': 'EN', 'zh': '中文'},

    # --- Login ---
    'login.username': {'en': 'Username', 'zh': '用户名'},
    'login.password': {'en': 'Password', 'zh': '密码'},
    'login.signin': {'en': 'Sign in', 'zh': '登录'},
    'login.google': {'en': 'Sign in with Google', 'zh': '使用 Google 登录'},
    'login.duo': {'en': 'Sign in with Duo', 'zh': '使用 Duo 登录'},

    # --- Dashboard ---
    'dash.title': {'en': 'Dashboard', 'zh': '仪表盘'},
    'dash.status': {'en': 'Status', 'zh': '状态'},
    'dash.devices': {'en': 'Devices', 'zh': '设备'},
    'dash.log': {'en': 'Log', 'zh': '日志'},
    'dash.recent': {'en': 'Recent log entries', 'zh': '最近日志'},

    # --- Servers ---
    'srv.title': {'en': 'Servers', 'zh': '服务器'},
    'srv.add': {'en': 'Add Server', 'zh': '添加服务器'},
    'srv.name': {'en': 'Name', 'zh': '名称'},
    'srv.port': {'en': 'Port', 'zh': '端口'},
    'srv.protocol': {'en': 'Protocol', 'zh': '协议'},
    'srv.network': {'en': 'Network', 'zh': '网络'},
    'srv.status': {'en': 'Status', 'zh': '状态'},
    'srv.actions': {'en': 'Actions', 'zh': '操作'},
    'srv.edit': {'en': 'Edit', 'zh': '编辑'},
    'srv.delete': {'en': 'Delete', 'zh': '删除'},
    'srv.bandwidth': {'en': 'Bandwidth', 'zh': '带宽'},
    'srv.output': {'en': 'Output', 'zh': '输出'},
    'srv.routes': {'en': 'Routes', 'zh': '路由'},
    'srv.organizations': {'en': 'Organizations', 'zh': '组织'},
    'srv.hosts': {'en': 'Hosts', 'zh': '主机'},
    'srv.links': {'en': 'Links', 'zh': '链接'},
    'srv.loadFailed': {'en': 'Failed to load servers, server error occurred.', 'zh': '加载服务器失败，服务器发生错误。'},
    'srv.addRoute': {'en': 'Add Route', 'zh': '添加路由'},
    'srv.attachOrg': {'en': 'Attach Organization', 'zh': '附加组织'},
    'srv.attachHost': {'en': 'Attach Host', 'zh': '附加主机'},
    'srv.linkServer': {'en': 'Link Server', 'zh': '链接服务器'},
    'srv.start': {'en': 'Start Server', 'zh': '启动服务器'},
    'srv.stop': {'en': 'Stop Server', 'zh': '停止服务器'},
    'srv.restart': {'en': 'Restart Server', 'zh': '重启服务器'},
    'srv.settings': {'en': 'Settings', 'zh': '设置'},
    'srv.outputClear': {'en': 'Click to clear server output', 'zh': '点击清除服务器输出'},
    'srv.outputLinkClear': {'en': 'Click to clear server link output', 'zh': '点击清除服务器链接输出'},
    'srv.bandwidthGraphs': {'en': 'Bandwidth Graphs', 'zh': '带宽图表'},
    'srv.linkOutput': {'en': 'Link Output', 'zh': '链接输出'},
    'srv.devices': {'en': 'Devices', 'zh': '设备'},
    'srv.networkLabel': {'en': 'Network', 'zh': '网络'},
    'srv.portLabel': {'en': 'Port', 'zh': '端口'},
    'srv.modeLabel': {'en': 'Multiple Devices', 'zh': '多设备'},
    'srv.uptimeLabel': {'en': 'Uptime', 'zh': '运行时间'},
    'srv.usersLabel': {'en': 'Users', 'zh': '用户'},
    'srv.dhWarning': {'en': 'Generating DH parameters, please wait...', 'zh': '正在生成 DH 参数，请稍候...'},
    'srv.noOrgWarning': {'en': 'Server must have an organization attached', 'zh': '服务器必须附加组织'},
    'srv.noHostWarning': {'en': 'Server must have a host attached', 'zh': '服务器必须附加主机'},
    'srv.noOrgHostWarning': {'en': 'Server must have a host and an organization attached', 'zh': '服务器必须同时附加主机和组织'},
    'srv.online': {'en': 'Online', 'zh': '在线'},
    'srv.offline': {'en': 'Offline', 'zh': '离线'},
    'srv.365days': {'en': '365 Days', 'zh': '365 天'},
    'srv.30days': {'en': '30 Days', 'zh': '30 天'},
    'srv.7days': {'en': '7 Days', 'zh': '7 天'},
    'srv.24hours': {'en': '24 Hours', 'zh': '24 小时'},
    'srv.6hours': {'en': '6 Hours', 'zh': '6 小时'},

    # --- Users ---
    'usr.title': {'en': 'Users', 'zh': '用户'},
    'usr.add': {'en': 'Add User', 'zh': '添加用户'},
    'usr.addBulk': {'en': 'Add Users (Bulk)', 'zh': '批量添加用户'},
    'usr.name': {'en': 'Name', 'zh': '名称'},
    'usr.email': {'en': 'Email', 'zh': '邮箱'},
    'usr.org': {'en': 'Organization', 'zh': '组织'},
    'usr.actions': {'en': 'Actions', 'zh': '操作'},
    'usr.edit': {'en': 'Edit', 'zh': '编辑'},
    'usr.delete': {'en': 'Delete', 'zh': '删除'},
    'usr.devices': {'en': 'Devices', 'zh': '设备'},
    'usr.servers': {'en': 'Servers', 'zh': '服务器'},
    'usr.download': {'en': 'Download', 'zh': '下载'},
    'usr.audit': {'en': 'Audit', 'zh': '审计'},
    'usr.disabled': {'en': 'Disabled', 'zh': '已禁用'},
    'usr.enabled': {'en': 'Enable user', 'zh': '启用用户'},
    'usr.disableDisconnect': {'en': 'Disable and disconnect user', 'zh': '禁用并断开用户'},
    'usr.settings': {'en': 'User settings', 'zh': '用户设置'},
    'usr.lastConnected': {'en': 'User last connected', 'zh': '用户最后连接时间'},
    'usr.dnsName': {'en': 'User dns name', 'zh': '用户 DNS 名称'},
    'usr.networkLinks': {'en': 'User network links', 'zh': '用户网络链接'},
    'usr.groups': {'en': 'User groups', 'zh': '用户组'},
    'usr.serverUser': {'en': 'Server user', 'zh': '服务器用户'},
    'usr.showInfo': {'en': 'Show additional user information', 'zh': '显示更多用户信息'},
    'usr.otpKey': {'en': 'Get two-step authentication key', 'zh': '获取两步验证密钥'},
    'usr.auditLabel': {'en': 'User audit', 'zh': '用户审计'},
    'usr.keyLink': {'en': 'Key link', 'zh': '密钥链接'},
    'usr.noServers': {'en': 'No servers available', 'zh': '暂无可用服务器'},
    'usr.noDevices': {'en': 'No devices available', 'zh': '暂无可用设备'},
    'usr.lastActive': {'en': 'Last Active', 'zh': '最后活跃'},
    'usr.lastActiveNever': {'en': 'Never', 'zh': '从未'},
    'usr.downloadKey': {'en': 'Download key', 'zh': '下载密钥'},
    'usr.virtualIp': {'en': 'User virtual IP address', 'zh': '用户虚拟 IP 地址'},
    'usr.realIp': {'en': 'User real IP address', 'zh': '用户真实 IP 地址'},
    'usr.connectedSince': {'en': 'Connected since', 'zh': '连接时间'},
    'usr.serverName': {'en': 'Server name', 'zh': '服务器名称'},
    'usr.deviceName': {'en': 'Device name', 'zh': '设备名称'},

    # --- Organizations ---
    'org.title': {'en': 'Organizations', 'zh': '组织'},
    'org.add': {'en': 'Add Organization', 'zh': '添加组织'},
    'org.name': {'en': 'Name', 'zh': '名称'},
    'org.users': {'en': 'Users', 'zh': '用户'},
    'org.actions': {'en': 'Actions', 'zh': '操作'},
    'org.edit': {'en': 'Edit', 'zh': '编辑'},
    'org.delete': {'en': 'Delete', 'zh': '删除'},
    'org.modify': {'en': 'Click to modify this organization', 'zh': '点击修改此组织'},
    'org.settings': {'en': 'Settings', 'zh': '设置'},
    'org.sortName': {'en': 'Name', 'zh': '名称'},
    'org.sortActive': {'en': 'Last Active', 'zh': '最后活跃'},
    'org.search': {'en': 'Search for user', 'zh': '搜索用户'},
    'org.ttlAlert': {'en': 'This organization must be recreated after expiration. Check organization expiration documentation for more information', 'zh': '此组织到期后必须重新创建。请查阅组织过期文档了解更多信息'},
    'org.noOrgs': {'en': 'There are no organizations attached to this server.', 'zh': '此服务器没有附加组织。'},
    'org.detachConfirm': {'en': 'Are you sure you want to detach the ', 'zh': '确定要分离 '},
    'org.deleteConfirm': {'en': 'Enter the name of the organization to confirm', 'zh': '请输入组织名称以确认'},
    'org.detachOrg': {'en': 'Detach Organization', 'zh': '分离组织'},
    'org.userCount': {'en': 'users', 'zh': '个用户'},
    'org.detachWarning': {'en': 'Deleting the organization will delete all the users', 'zh': '删除组织将删除所有用户'},

    # --- Hosts ---
    'host.title': {'en': 'Hosts', 'zh': '主机'},
    'host.add': {'en': 'Add Host', 'zh': '添加主机'},
    'host.name': {'en': 'Name', 'zh': '名称'},
    'host.status': {'en': 'Status', 'zh': '状态'},
    'host.usage': {'en': 'Usage', 'zh': '使用率'},
    'host.actions': {'en': 'Actions', 'zh': '操作'},
    'host.edit': {'en': 'Edit', 'zh': '编辑'},
    'host.delete': {'en': 'Delete', 'zh': '删除'},
    'host.settings': {'en': 'Settings', 'zh': '设置'},
    'host.uptime': {'en': 'Uptime', 'zh': '运行时间'},
    'host.users': {'en': 'Users', 'zh': '用户'},
    'host.publicIp': {'en': 'Public IP', 'zh': '公网 IP'},
    'host.localIp': {'en': 'Local IP', 'zh': '内网 IP'},
    'host.cpuUsage': {'en': 'CPU Usage', 'zh': 'CPU 使用率'},
    'host.memUsage': {'en': 'Memory Usage', 'zh': '内存使用率'},
    'host.online': {'en': 'Online', 'zh': '在线'},
    'host.offline': {'en': 'Offline', 'zh': '离线'},
    'host.clickSettings': {'en': 'Click to open host settings', 'zh': '点击打开主机设置'},
    'host.mustOffline': {'en': 'Host must be offline to delete', 'zh': '主机必须离线才能删除'},
    'host.usersOnline': {'en': 'users online', 'zh': '个用户在线'},
    'host.deleteConfirm': {'en': 'Enter the name of the host to confirm', 'zh': '请输入主机名称以确认'},
    'host.noHosts': {'en': 'There are no hosts attached to this server.', 'zh': '此服务器没有附加主机。'},
    'host.detachHost': {'en': 'Detach Host', 'zh': '分离主机'},
    'host.detachConfirm': {'en': 'Are you sure you want to detach the ', 'zh': '确定要分离 '},
    'host.saved': {'en': 'Successfully saved host settings.', 'zh': '主机设置已成功保存。'},
    'host.noHostsAttach': {'en': 'No hosts exist, a host must be created before attaching.', 'zh': '不存在主机，必须先创建主机才能附加。'},
    'host.mustOfflineDetach': {'en': 'Server must be offline to detach an organization.', 'zh': '服务器必须离线才能分离组织。'},
    'host.loadFailed': {'en': 'Failed to load hosts, server error occurred.', 'zh': '加载主机失败，服务器发生错误。'},

    # --- Links ---
    'lnk.title': {'en': 'Links', 'zh': '链接'},
    'lnk.add': {'en': 'Add Link', 'zh': '添加链接'},
    'lnk.addLocation': {'en': 'Add Location', 'zh': '添加位置'},
    'lnk.name': {'en': 'Name', 'zh': '名称'},
    'lnk.status': {'en': 'Status', 'zh': '状态'},
    'lnk.actions': {'en': 'Actions', 'zh': '操作'},
    'lnk.edit': {'en': 'Edit', 'zh': '编辑'},
    'lnk.delete': {'en': 'Delete', 'zh': '删除'},
    'lnk.locations': {'en': 'Locations', 'zh': '位置'},
    'lnk.peer': {'en': 'Peer', 'zh': '对等节点'},
    'lnk.transit': {'en': 'Transit', 'zh': '传输节点'},
    'lnk.route': {'en': 'Route', 'zh': '路由'},
    'lnk.direct': {'en': 'Direct', 'zh': '直连'},
    'lnk.siteToSite': {'en': 'Site-To-Site', 'zh': '站点到站点'},
    'lnk.clickSettings': {'en': 'Click to open link settings', 'zh': '点击打开链接设置'},
    'lnk.delLink': {'en': 'Delete Link', 'zh': '删除链接'},
    'lnk.stopLink': {'en': 'Stop Link', 'zh': '停止链接'},
    'lnk.startLink': {'en': 'Start Link', 'zh': '启动链接'},
    'lnk.rekeyLink': {'en': 'Rekey Link', 'zh': '重新密钥链接'},
    'lnk.settings': {'en': 'Settings', 'zh': '设置'},
    'lnk.lan': {'en': 'LAN', 'zh': '局域网'},
    'lnk.online': {'en': 'Online', 'zh': '在线'},
    'lnk.offline': {'en': 'Offline', 'zh': '离线'},
    'lnk.unlink': {'en': 'Unlink Server', 'zh': '取消链接服务器'},
    'lnk.noLinks': {'en': 'There are no links on this system.', 'zh': '此系统没有链接。'},
    'lnk.addPeer': {'en': 'Add Peer', 'zh': '添加对等节点'},
    'lnk.addHost': {'en': 'Add Host', 'zh': '添加主机'},
    'lnk.addRoute': {'en': 'Add Route', 'zh': '添加路由'},
    'lnk.deleteLocation': {'en': 'Delete Location', 'zh': '删除位置'},
    'lnk.locationSettings': {'en': 'Settings', 'zh': '设置'},
    'lnk.noLocations': {'en': 'There are no locations on this link.', 'zh': '此链接没有位置。'},
    'lnk.noRoutes': {'en': 'There are no routes on this location.', 'zh': '此位置没有路由。'},
    'lnk.noHosts': {'en': 'There are no hosts on this location.', 'zh': '此位置没有主机。'},
    'lnk.removeRoute': {'en': 'Remove Route', 'zh': '移除路由'},
    'lnk.clickModifyHost': {'en': 'Click to modify this host', 'zh': '点击修改此主机'},
    'lnk.interlinkLatency': {'en': 'Interlink Latency', 'zh': '互联延迟'},
    'lnk.unknown': {'en': 'unknown', 'zh': '未知'},
    'lnk.static': {'en': 'Static', 'zh': '静态'},
    'lnk.active': {'en': 'Active', 'zh': '活跃'},
    'lnk.available': {'en': 'Available', 'zh': '可用'},
    'lnk.activeUnavailable': {'en': 'Active Unavailable', 'zh': '活跃不可用'},
    'lnk.unavailable': {'en': 'Unavailable', 'zh': '不可用'},
    'lnk.getConf': {'en': 'Get Conf', 'zh': '获取配置'},
    'lnk.getEdgeRouterConf': {'en': 'Get EdgeRouter Conf', 'zh': '获取 EdgeRouter 配置'},
    'lnk.getUri': {'en': 'Get URI', 'zh': '获取 URI'},
    'lnk.settingsHost': {'en': 'Settings', 'zh': '设置'},
    'lnk.removeHost': {'en': 'Remove Host', 'zh': '移除主机'},
    'lnk.connected': {'en': 'Connected', 'zh': '已连接'},
    'lnk.connecting': {'en': 'Connecting', 'zh': '连接中'},
    'lnk.disconnected': {'en': 'Disconnected', 'zh': '已断开'},
    'lnk.transitConnected': {'en': 'Transit', 'zh': '传输'},
    'lnk.transitPeer': {'en': 'Transit Peer', 'zh': '传输对等节点'},
    'lnk.untransitPeer': {'en': 'Untransit Peer', 'zh': '取消传输对等节点'},
    'lnk.removePeer': {'en': 'Remove Peer', 'zh': '移除对等节点'},
    'lnk.transitConfirm': {'en': 'Are you sure you want to transit the ', 'zh': '确定要传输 '},
    'lnk.untransitConfirm': {'en': 'Are you sure you want to untransit the ', 'zh': '确定要取消传输 '},
    'lnk.removeConfirm': {'en': 'Are you sure you want to remove the ', 'zh': '确定要移除 '},
    'lnk.addLocationTitle': {'en': 'Add Location', 'zh': '添加位置'},
    'lnk.locationTitle': {'en': 'Location', 'zh': '位置'},

    # --- Admins ---
    'adm.title': {'en': 'Administrators', 'zh': '管理员'},
    'adm.add': {'en': 'Add Administrator', 'zh': '添加管理员'},
    'adm.name': {'en': 'Name', 'zh': '名称'},
    'adm.email': {'en': 'Email', 'zh': '邮箱'},
    'adm.actions': {'en': 'Actions', 'zh': '操作'},
    'adm.edit': {'en': 'Edit', 'zh': '编辑'},
    'adm.delete': {'en': 'Delete', 'zh': '删除'},
    'adm.audit': {'en': 'Audit', 'zh': '审计'},
    'adm.superUser': {'en': 'Super User', 'zh': '超级用户'},
    'adm.clickModify': {'en': 'Click to modify this administrator', 'zh': '点击修改此管理员'},
    'adm.otpKey': {'en': 'Get two-step authentication key', 'zh': '获取两步验证密钥'},
    'adm.auditLabel': {'en': 'Administrator audit', 'zh': '管理员审计'},
    'adm.disable': {'en': 'Disable and logout administrator', 'zh': '禁用并退出管理员'},
    'adm.settings': {'en': 'Administrator settings', 'zh': '管理员设置'},
    'adm.enable': {'en': 'Enable administrator', 'zh': '启用管理员'},
    'adm.added': {'en': 'Successfully added administrator.', 'zh': '管理员已成功添加。'},
    'adm.deleteSelected': {'en': 'Successfully deleted selected administrators.', 'zh': '已成功删除所选管理员。'},

    # --- Settings ---
    'set.title': {'en': 'Settings', 'zh': '设置'},
    'set.general': {'en': 'General', 'zh': '通用'},
    'set.email': {'en': 'Email', 'zh': '邮件'},
    'set.monitoring': {'en': 'Monitoring', 'zh': '监控'},
    'set.save': {'en': 'Save', 'zh': '保存'},
    'set.saved': {'en': 'Successfully saved settings.', 'zh': '设置已成功保存。'},
    'set.failed': {'en': 'Failed to load settings data, server error occurred.', 'zh': '加载设置数据失败，服务器发生错误。'},
    'set.username': {'en': 'Username', 'zh': '用户名'},
    'set.newPassword': {'en': 'New Password', 'zh': '新密码'},
    'set.auditingMode': {'en': 'Auditing Mode', 'zh': '审计模式'},
    'set.disabled': {'en': 'Disabled', 'zh': '已禁用'},
    'set.all': {'en': 'All', 'zh': '全部'},
    'set.pinMode': {'en': 'Pin Mode', 'zh': 'PIN 模式'},
    'set.optional': {'en': 'Optional', 'zh': '可选'},
    'set.required': {'en': 'Required', 'zh': '必填'},
    'set.publicAddress': {'en': 'Public Address', 'zh': '公网地址'},
    'set.theme': {'en': 'Theme', 'zh': '主题'},
    'set.light': {'en': 'Light', 'zh': '浅色'},
    'set.dark': {'en': 'Dark', 'zh': '深色'},
    'set.webPort': {'en': 'Web Console Port', 'zh': 'Web 控制台端口'},
    'set.reverseProxy': {'en': 'Allow Reverse Proxy', 'zh': '允许反向代理'},
    'set.sso': {'en': 'Single Sign-On', 'zh': '单点登录'},
    'set.ssoDomain': {'en': 'Single Sign-On Domain', 'zh': '单点登录域名'},
    'set.ssoOrg': {'en': 'Default Single Sign-On Organization', 'zh': '默认单点登录组织'},
    'set.ipv6': {'en': 'Accept IPv6 Connections', 'zh': '接受 IPv6 连接'},
    'set.openvpnCache': {'en': 'OpenVPN Authentication Cache', 'zh': 'OpenVPN 认证缓存'},
    'set.pritunlCache': {'en': 'Pritunl Authentication Cache', 'zh': 'Pritunl 认证缓存'},
    'set.restrictImport': {'en': 'Restrict Profile Import', 'zh': '限制配置文件导入'},
    'set.publicIpv6': {'en': 'Public IPv6 Address', 'zh': '公网 IPv6 地址'},
    'set.routedSubnet6': {'en': 'Routed IPv6 Subnet', 'zh': '路由 IPv6 子网'},
    'set.routedWgSubnet6': {'en': 'Routed WG IPv6 Subnet', 'zh': '路由 WG IPv6 子网'},
    'set.monitoringMode': {'en': 'Monitoring Mode', 'zh': '监控模式'},
    'set.influxdb': {'en': 'InfluxDB', 'zh': 'InfluxDB'},
    'set.acmeDomain': {'en': 'Lets Encrypt Domain', 'zh': "Let's Encrypt 域名"},
    'set.cloudProvider': {'en': 'Cloud Provider', 'zh': '云服务商'},
    'set.none': {'en': 'None', 'zh': '无'},
    'set.aws': {'en': 'AWS', 'zh': 'AWS'},
    'set.oracle': {'en': 'Oracle', 'zh': 'Oracle'},
    'set.pritunlCloud': {'en': 'Pritunl Cloud', 'zh': 'Pritunl 云'},
    'set.clientReconnect': {'en': 'Enable Client Reconnect', 'zh': '启用客户端重连'},
    'set.restrictClient': {'en': 'Restrict Pritunl Client Options', 'zh': '限制 Pritunl 客户端选项'},
    'set.dropPermissions': {'en': 'Drop OpenVPN Permissions', 'zh': '降低 OpenVPN 权限'},
    'set.smtpFrom': {'en': 'SMTP From Address', 'zh': 'SMTP 发件人地址'},
    'set.smtpUsername': {'en': 'SMTP Username', 'zh': 'SMTP 用户名'},
    'set.smtpServer': {'en': 'SMTP Server', 'zh': 'SMTP 服务器'},
    'set.smtpPassword': {'en': 'SMTP Password', 'zh': 'SMTP 密码'},
    'set.serverCert': {'en': 'Server SSL Certificate', 'zh': '服务器 SSL 证书'},
    'set.serverKey': {'en': 'Server SSL Key', 'zh': '服务器 SSL 密钥'},
    'set.influxdbUrl': {'en': 'InfluxDB URL', 'zh': 'InfluxDB 地址'},
    'set.influxdbToken': {'en': 'InfluxDB Token', 'zh': 'InfluxDB 令牌'},
    'set.influxdbOrg': {'en': 'InfluxDB Org', 'zh': 'InfluxDB 组织'},
    'set.influxdbBucket': {'en': 'InfluxDB Bucket', 'zh': 'InfluxDB 存储桶'},
    'set.autoRoute53': {'en': 'Auto Route 53 Region', 'zh': '自动 Route 53 区域'},
    'set.autoRoute53Zone': {'en': 'Auto Route 53 Zone', 'zh': '自动 Route 53 区域组'},
    'set.oracleUserOcid': {'en': 'Oracle User OCID', 'zh': 'Oracle 用户 OCID'},
    'set.oraclePublicKey': {'en': 'Oracle API Public Key', 'zh': 'Oracle API 公钥'},
    'set.pritunlCloudToken': {'en': 'Pritunl Cloud Token', 'zh': 'Pritunl 云令牌'},
    'set.pritunlCloudHost': {'en': 'Pritunl Cloud Host', 'zh': 'Pritunl 云主机'},
    'set.pritunlCloudSecret': {'en': 'Pritunl Cloud Secret', 'zh': 'Pritunl 云密钥'},

    # --- Logs ---
    'log.title': {'en': 'Logs', 'zh': '日志'},
    'log.filter': {'en': 'Filter', 'zh': '筛选'},
    'log.recent': {'en': 'Recent log entries', 'zh': '最近日志'},

    # --- Common ---
    'common.yes': {'en': 'Yes', 'zh': '是'},
    'common.no': {'en': 'No', 'zh': '否'},
    'common.confirm': {'en': 'Confirm', 'zh': '确认'},
    'common.cancel': {'en': 'Cancel', 'zh': '取消'},
    'common.close': {'en': 'Close', 'zh': '关闭'},
    'common.required': {'en': 'Required', 'zh': '必填'},
    'common.optional': {'en': 'Optional', 'zh': '可选'},
    'common.enabled': {'en': 'Enabled', 'zh': '已启用'},
    'common.disabled': {'en': 'Disabled', 'zh': '已禁用'},
    'common.active': {'en': 'Active', 'zh': '活跃'},
    'common.inactive': {'en': 'Inactive', 'zh': '非活跃'},
    'common.online': {'en': 'Online', 'zh': '在线'},
    'common.offline': {'en': 'Offline', 'zh': '离线'},
    'common.connected': {'en': 'Connected', 'zh': '已连接'},
    'common.disconnected': {'en': 'Disconnected', 'zh': '已断开'},
    'common.connecting': {'en': 'Connecting', 'zh': '连接中'},
    'common.available': {'en': 'Available', 'zh': '可用'},
    'common.unavailable': {'en': 'Unavailable', 'zh': '不可用'},
    'common.none': {'en': 'None', 'zh': '无'},
    'common.all': {'en': 'All', 'zh': '全部'},
    'common.loading': {'en': 'Loading...', 'zh': '加载中...'},
    'common.error': {'en': 'Error', 'zh': '错误'},
    'common.success': {'en': 'Success', 'zh': '成功'},
    'common.warning': {'en': 'Warning', 'zh': '警告'},
    'common.deleteConfirm': {'en': 'Are you sure?', 'zh': '确定要删除吗？'},
    'common.deleteSelected': {'en': 'Delete Selected', 'zh': '删除选中'},
    'common.prev': {'en': 'Previous', 'zh': '上一页'},
    'common.next': {'en': 'Next', 'zh': '下一页'},
    'common.first': {'en': 'First', 'zh': '首页'},
    'common.last': {'en': 'Last', 'zh': '末页'},
    'common.add': {'en': 'Add', 'zh': '添加'},
    'common.edit': {'en': 'Edit', 'zh': '编辑'},
    'common.view': {'en': 'View', 'zh': '查看'},
    'common.search': {'en': 'Search', 'zh': '搜索'},
    'common.showMore': {'en': 'show more results', 'zh': '显示更多结果'},
    'common.remove': {'en': 'Remove', 'zh': '移除'},
    'common.noData': {'en': 'There is no data.', 'zh': '暂无数据。'},
    'common.sessionExpired': {'en': 'Session has expired, please log in again', 'zh': '会话已过期，请重新登录'},
    'common.logoutFailed': {'en': 'Failed to logout, server error occurred.', 'zh': '退出登录失败，服务器发生错误。'},
    'common.authFailed': {'en': 'Failed to load authentication data, server error occurred.', 'zh': '加载认证数据失败，服务器发生错误。'},
    'common.loadFailed': {'en': 'Failed to load, server error occurred.', 'zh': '加载失败，服务器发生错误。'},
    'common.save': {'en': 'Save', 'zh': '保存'},
    'common.cancel': {'en': 'Cancel', 'zh': '取消'},
    'common.close': {'en': 'Close', 'zh': '关闭'},
    'common.advanced': {'en': 'Advanced', 'zh': '高级'},

    # --- Server status ---
    'status.online': {'en': 'Online', 'zh': '在线'},
    'status.offline': {'en': 'Offline', 'zh': '离线'},
    'status.connecting': {'en': 'Connecting', 'zh': '连接中'},
    'status.disconnected': {'en': 'Disconnected', 'zh': '已断开'},

    # --- Alerts ---
    'alert.success': {'en': 'Success', 'zh': '成功'},
    'alert.danger': {'en': 'Error', 'zh': '错误'},
    'alert.warning': {'en': 'Warning', 'zh': '警告'},
    'alert.info': {'en': 'Info', 'zh': '提示'},
    'alert.dismiss': {'en': 'Dismiss', 'zh': '关闭'},

    # --- Devices ---
    'dev.unregistered': {'en': 'Unregistered Devices', 'zh': '未注册设备'},
    'dev.register': {'en': 'Register', 'zh': '注册'},
    'dev.devices': {'en': 'Devices', 'zh': '设备'},
    'dev.pending': {'en': 'Devices Pending Registration', 'zh': '待注册设备'},
    'dev.noPending': {'en': 'There are no pending devices.', 'zh': '没有待处理设备。'},
    'dev.registerDevice': {'en': 'Register Device', 'zh': '注册设备'},
    'dev.removeDevice': {'en': 'Remove Device', 'zh': '移除设备'},
    'dev.regKey': {'en': 'Registration Key', 'zh': '注册密钥'},
    'dev.registered': {'en': 'Successfully registered device.', 'zh': '设备已成功注册。'},
    'dev.removeConfirm': {'en': 'Are you sure you want to remove the ', 'zh': '确定要移除 '},

    # --- Links upgrade ---
    'lnk.upgrade': {'en': 'Upgrade to Enterprise+ for site-to-site links with IPsec', 'zh': '升级到 Enterprise+ 以使用 IPsec 站点到站点链接'},

    # --- Modal ---
    'modal.advanced': {'en': 'Advanced', 'zh': '高级'},
    'modal.confirm': {'en': 'Confirm', 'zh': '确认'},
    'modal.cancel': {'en': 'Cancel', 'zh': '取消'},
    'modal.save': {'en': 'Save', 'zh': '保存'},
    'modal.add': {'en': 'Add', 'zh': '添加'},
    'modal.edit': {'en': 'Edit', 'zh': '编辑'},
    'modal.delete': {'en': 'Delete', 'zh': '删除'},
    'modal.close': {'en': 'Close', 'zh': '关闭'},
    'modal.ok': {'en': 'OK', 'zh': '确定'},

    # --- Host Usage ---
    'hostUsage.cpu': {'en': 'CPU Usage', 'zh': 'CPU 使用率'},
    'hostUsage.memory': {'en': 'Memory Usage', 'zh': '内存使用率'},

    # --- Server Bandwidth ---
    'srvBw.received': {'en': 'Received', 'zh': '接收'},
    'srvBw.sent': {'en': 'Sent', 'zh': '发送'},
}

# Read current i18n/index.js
with open('www/i18n/index.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position of the last closing brace of translations object
# We need to insert new keys before the closing brace
# Find the last } before the var currentLang line
insert_pos = content.find('var currentLang')
if insert_pos == -1:
    print("ERROR: Could not find insertion point")
    exit(1)

# Build the new keys to insert
new_keys = []
for key, trans in sorted(TRANSLATIONS.items()):
    new_keys.append(f"      '{key}': '{trans['en']}',")

# Insert new English keys
new_en_block = '\n' + '\n'.join(new_keys) + '\n    '
content = content[:insert_pos] + new_en_block + content[insert_pos:]

# Now add Chinese translations
# Find the position after the English block closing
zh_insert_pos = content.find("    zh: {")
if zh_insert_pos == -1:
    print("ERROR: Could not find zh block")
    exit(1)

# Find the closing of zh block
zh_block_end = content.find('    };', zh_insert_pos)
if zh_block_end == -1:
    print("ERROR: Could not find zh block end")
    exit(1)

# Build Chinese keys
zh_keys = []
for key, trans in sorted(TRANSLATIONS.items()):
    zh_keys.append(f"      '{key}': '{trans['zh']}',")

new_zh_block = '\n' + '\n'.join(zh_keys) + '\n    '
content = content[:zh_block_end] + new_zh_block + content[zh_block_end:]

# Write back
with open('www/i18n/index.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Added {len(TRANSLATIONS)} translation keys to i18n/index.js")
