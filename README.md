# pritunl - 企业级 VPN 服务器

[![github](https://img.shields.io/badge/github-pritunl-181717.svg?style=flat)](https://github.com/pritunl)
[![twitter](https://img.shields.io/badge/twitter-pritunl-55acee.svg?style=flat)](https://twitter.com/pritunl)
[![substack](https://img.shields.io/badge/substack-pritunl-ff6719.svg?style=flat)](https://pritunl.substack.com/)
[![forum](https://img.shields.io/badge/discussion-forum-ffffff.svg?style=flat)](https://forum.pritunl.com)

[Pritunl](https://github.com/pritunl/pritunl) 是一个基于 OpenVPN 协议构建的分布式企业级 VPN 服务器。更多信息和文档请访问官网 [pritunl.com](https://pritunl.com)

[![pritunl](www/img/logo_code.png)](https://pritunl.com)

---

## Docker 部署（推荐）

本项目已内置 Docker 构建文件，使用 Docker Compose 即可一键启动完整的 Pritunl 服务（包含 MongoDB、Redis）。

### 前置要求

- Docker Engine >= 20.10
- Docker Compose >= 2.0
- 主机需开放端口：**443/tcp**（Web UI / API）、**1194/udp**（OpenVPN 主用）、**1194/tcp**（OpenVPN 备用）
- 宿主机需开启 IPv4 转发：`sysctl net.ipv4.ip_forward=1`

### 快速启动

```bash
# 1. 进入项目目录
cd E:\Git\OpenSource\pritunl

# 2. 复制环境变量模板（可选）
copy .env.example .env

# 3. 根据实际情况修改 .env 中的 MongoDB / Redis 连接地址

# 4. 启动所有服务
docker compose up -d

# 5. 查看 Pritunl 日志
docker compose logs -f pritunl
```

### 首次使用

容器启动后，通过浏览器访问 `https://<服务器IP>:443` 进入 Pritunl Web 管理界面。

首次登录时系统会提示设置管理员账户和 MongoDB 连接信息。

### 服务说明

| 服务 | 镜像 | 说明 |
|---|---|---|
| `pritunl` | 本地构建 | Pritunl VPN 主服务（Python 后端 + Go 前端） |
| `mongodb` | `mongo:8.0` | 数据存储 |
| `redis` | `redis:8-alpine` | 缓存服务（可选，提升性能） |

### 数据持久化

以下数据卷在容器销毁后仍然保留：

- `mongodb_data` - MongoDB 数据库
- `redis_data` - Redis 缓存
- `pritunl_data` - Pritunl 证书、密钥、配置
- `pritunl_logs` - 日志文件

### 常用操作

```bash
# 停止服务
docker compose down

# 停止并删除所有数据（全新开始）
docker compose down -v

# 重新构建镜像后启动
docker compose build --no-cache
docker compose up -d

# 进入容器调试
docker compose exec pritunl bash
```

### 环境变量

在 `.env` 文件中可配置以下变量：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `PRITUNL_MONGODB_URI` | `mongodb://mongodb:27017/pritunl` | MongoDB 连接地址 |
| `PRITUNL_REDIS_URI` | `redis://redis:6379/0` | Redis 连接地址 |
| `PRITUNL_CONF` | `/etc/pritunl.conf` | 配置文件路径 |

### 注意事项

- 本项目为修改版 Pritunl，已移除 Enterprise 功能，增加了中英文双语界面。
- Docker 容器以非 root 用户 `pritunl` 运行，增强了安全性。
- OpenVPN 需要宿主机开启 IPv4 转发，Docker Compose 已自动配置 `net.ipv4.ip_forward=1`。

---

## 从源码安装

> 注意：以下为官方 Pritunl 的源码安装流程，仅作参考。

```bash
# 安装 MongoDB（单主机配置）
sudo tee /etc/yum.repos.d/mongodb-org.repo << EOF
[mongodb-org]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/9/mongodb-org/8.2/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-8.0.asc
EOF

sudo dnf -y install mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# 安装 OpenVPN
sudo tee /etc/yum.repos.d/pritunl.repo << EOF
[pritunl]
name=Pritunl Repository
baseurl=https://repo.pritunl.com/stable/yum/oraclelinux/9/
gpgcheck=1
enabled=1
gpgkey=https://raw.githubusercontent.com/pritunl/pgp/master/pritunl_repo_pub.asc
EOF

sudo dnf --allowerasing -y install pritunl-openvpn

# [可选] 安装 ndppd 用于 IPv6 NDP 代理
sudo dnf -y install pritunl-ndppd

# 设置当前 pritunl 版本号 X.XX.XXXX.XX
export VERSION="X.XX.XXXX.XX"

sudo dnf -y install gcc git-core wget rsync openssl-devel bzip2-devel libffi-devel sqlite-devel xz-devel zlib-devel selinux-policy selinux-policy-devel policycoreutils-python-utils python3 net-tools openssl iptables ipset ca-certificates psmisc

wget https://www.python.org/ftp/python/3.12.13/Python-3.12.13.tgz
echo "a7438eabd3a48139f42d4e058096af8d880b0bb6e8fb8c78838892e4ce5583f2 Python-3.12.13.tgz" | sha256sum -c - && tar xf Python-3.12.13.tgz
rm Python-3.12.13.tgz

cd "./Python-3.12.13"
gcc_major=$(gcc -dumpversion | cut -d. -f1)
base_cflags="-fstack-protector-strong -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -Werror=format-security -mtune=generic -grecord-gcc-switches"
if [ "$gcc_major" -ge 7 ]; then
    gcc7_flags="-fno-semantic-interposition"
    cflags="$base_cflags $gcc7_flags"
    ldflags="-fno-semantic-interposition"
else
    cflags="$base_cflags"
    ldflags=""
fi
if [ "$gcc_major" -ge 8 ]; then
    gcc8_flags="-fstack-clash-protection -fcf-protection"
    cflags="$cflags $gcc8_flags"
fi
if [ "$gcc_major" -ge 11 ]; then
    arch_flags="-march=x86-64-v2"
    cflags="$cflags $arch_flags"
fi
export CFLAGS_NODIST="$cflags"
export LDFLAGS_NODIST="$ldflags"
sudo rm -rf /usr/lib/pritunl
sudo mkdir /usr/lib/pritunl
./configure --prefix=/usr/lib/pritunl/usr --libdir=/usr/lib/pritunl/usr/lib --enable-optimizations --enable-ipv6 --enable-loadable-sqlite-extensions --disable-shared --with-lto --with-computed-gotos=yes --with-platlibdir=lib
sudo make ENSUREPIP=no install
sudo /usr/lib/pritunl/usr/bin/python3 -m ensurepip
cd ../
sudo rm -rf ./Python-3.12.13

sudo rm -rf /usr/local/go
wget https://go.dev/dl/go1.26.1.linux-amd64.tar.gz
echo "031f088e5d955bab8657ede27ad4e3bc5b7c1ba281f05f245bcc304f327c987a go1.26.1.linux-amd64.tar.gz" | sha256sum -c - && sudo tar -C /usr/local -xf go1.26.1.linux-amd64.tar.gz
rm -f go1.26.1.linux-amd64.tar.gz

tee -a ~/.bashrc << 'EOF'
export GOPATH=$HOME/go
export GOROOT=/usr/local/go
export PATH=/usr/local/go/bin:$PATH
EOF
source ~/.bashrc

sudo systemctl stop pritunl || true

sudo mkdir -p /var/lib/pritunl

go install -v github.com/pritunl/pritunl-web@latest
go install -v github.com/pritunl/pritunl-dns@latest
sudo rm -f /usr/bin/pritunl-dns
sudo rm -f /usr/bin/pritunl-web
sudo cp -f ~/go/bin/pritunl-dns /usr/bin/pritunl-dns
sudo cp -f ~/go/bin/pritunl-web /usr/bin/pritunl-web

wget https://github.com/pritunl/pritunl/archive/refs/tags/$VERSION.tar.gz
tar xf $VERSION.tar.gz
rm $VERSION.tar.gz
cd ./pritunl-$VERSION
sudo /usr/lib/pritunl/usr/bin/pip3 install --require-hashes -r requirements-build.txt
sudo /usr/lib/pritunl/usr/bin/pip3 install --require-hashes -r requirements.txt
/usr/lib/pritunl/usr/bin/python3 setup.py build
sudo /usr/lib/pritunl/usr/bin/python3 setup.py install
sudo ln -sf /usr/lib/pritunl/usr/bin/pritunl /usr/bin/pritunl

sudo groupadd -r pritunl-web || true
sudo useradd -r -g pritunl-web -s /sbin/nologin -c 'Pritunl web server' pritunl-web || true

# [可选] SELinux 配置
cd selinux9
ln -s /usr/share/selinux/devel/Makefile
make
sudo make load
sudo cp pritunl.pp /usr/share/selinux/packages/pritunl.pp
sudo cp pritunl_dns.pp /usr/share/selinux/packages/pritunl_dns.pp
sudo cp pritunl_web.pp /usr/share/selinux/packages/pritunl_web.pp
sudo semodule -i /usr/share/selinux/packages/pritunl.pp /usr/share/selinux/packages/pritunl_dns.pp /usr/share/selinux/packages/pritunl_web.pp
sudo restorecon -v -R /tmp/pritunl* || true
sudo restorecon -v -R /run/pritunl* || true
sudo restorecon -v /etc/systemd/system/pritunl.service || true
sudo restorecon -v /usr/lib/systemd/system/pritunl.service || true
sudo restorecon -v /etc/systemd/system/pritunl-web.service || true
sudo restorecon -v /usr/lib/systemd/system/pritunl-web.service || true
sudo restorecon -v /usr/lib/pritunl/bin/pritunl || true
sudo restorecon -v /usr/lib/pritunl/bin/python || true
sudo restorecon -v /usr/lib/pritunl/bin/python3 || true
sudo restorecon -v /usr/lib/pritunl/bin/python3.6 || true
sudo restorecon -v /usr/lib/pritunl/bin/python3.9 || true
sudo restorecon -v /usr/lib/pritunl/usr/bin/pritunl || true
sudo restorecon -v /usr/lib/pritunl/usr/bin/python || true
sudo restorecon -v /usr/lib/pritunl/usr/bin/python3 || true
sudo restorecon -v /usr/lib/pritunl/usr/bin/python3.6 || true
sudo restorecon -v /usr/lib/pritunl/usr/bin/python3.9 || true
sudo restorecon -v /usr/bin/pritunl-web || true
sudo restorecon -v /usr/bin/pritunl-dns || true
sudo restorecon -v -R /var/lib/pritunl || true
sudo restorecon -v /var/log/pritunl* || true

cd ../../
sudo rm -rf ./pritunl-$VERSION

sudo systemctl daemon-reload
sudo systemctl start pritunl
sudo systemctl enable pritunl
```

## 许可证

请参阅 [`LICENSE`](LICENSE) 文件获取许可证副本。
