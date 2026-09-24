#!/bin/bash
# Entrypoint script for Pritunl Docker container
# Updates configuration from environment variables before starting the service

set -e

CONF_FILE="${PRITUNL_CONF:-/etc/pritunl.conf}"
MONGODB_URI="${PRITUNL_MONGODB_URI:-mongodb://localhost:27017/pritunl}"

update_config() {
    python3 << PYEOF
import json, os

conf_file = os.environ.get('PRITUNL_CONF', '/etc/pritunl.conf')
mongodb_uri = os.environ.get('PRITUNL_MONGODB_URI', 'mongodb://localhost:27017/pritunl')

with open(conf_file) as f:
    conf = json.load(f)

current_uri = conf.get('mongodb_uri', '')
if current_uri != mongodb_uri:
    print("Updating MongoDB URI to: %s" % mongodb_uri)
    conf['mongodb_uri'] = mongodb_uri
    with open(conf_file, 'w') as f:
        json.dump(conf, f, indent=4)
    print("Configuration updated successfully")
else:
    print("MongoDB URI already set to: %s" % mongodb_uri)
PYEOF
}

# Update configuration
if [ -f "$CONF_FILE" ]; then
    PRITUNL_CONF="$CONF_FILE" PRITUNL_MONGODB_URI="$MONGODB_URI" update_config
else
    echo "Creating config file at $CONF_FILE"
    mkdir -p "$(dirname "$CONF_FILE")"
    cat > "$CONF_FILE" << EOF
{
    "debug": false,
    "bind_addr": "0.0.0.0",
    "port": 443,
    "log_path": "/var/log/pritunl.log",
    "temp_path": "/tmp/pritunl_%r",
    "local_address_interface": "auto",
    "mongodb_uri": "$MONGODB_URI"
}
EOF
    chown pritunl:pritunl "$CONF_FILE"
fi

# Ensure directories exist
mkdir -p /var/log/pritunl /var/lib/pritunl

# Handle command arguments
if [ "$1" = "pritunl" ]; then
    shift
    exec pritunl "$@"
else
    exec "$@"
fi
