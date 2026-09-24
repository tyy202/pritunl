# Dockerfile for Pritunl VPN Server (modified open-source version)
# Architecture:
#   Stage 1 (web-builder): Build pritunl-web (Go frontend server)
#   Stage 2 (final): Python 3.12 runtime with all dependencies
#
# Build: docker build -t pritunl-custom .
# Run:   docker compose up -d

# ============================================================================
# Stage 1: Build pritunl-web (Go binary)
# ============================================================================
FROM golang:1.24-bookworm AS web-builder

WORKDIR /build

# Install git for fetching Go modules
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Build pritunl-web from the official Pritunl repository
# This Go binary serves the frontend static files and proxies API requests
RUN go install -v github.com/pritunl/pritunl-web@latest

# ============================================================================
# Stage 2: Final runtime image
# ============================================================================
FROM python:3.12-slim-bookworm

WORKDIR /app

# Environment settings
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies:
#   - openvpn: VPN server
#   - iptables/ipset: firewall and routing rules
#   - build-essential/gcc: compile Python C extensions (cryptography)
#   - libssl-dev/libffi-dev: required by cryptography package
#   - curl: health checks and downloads
#   - net-tools/procps: networking utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    openvpn \
    iptables ipset \
    net-tools procps \
    build-essential gcc \
    libssl-dev libffi-dev \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy pritunl-web binary from builder stage
COPY --from=web-builder /go/bin/pritunl-web /usr/local/bin/pritunl-web

# Copy application source code
COPY pritunl/ ./pritunl/
COPY www/ ./www/
COPY data/ ./data/
COPY requirements.txt ./
COPY setup.py ./
COPY server.py ./
COPY docker-entrypoint.sh /usr/local/bin/

# Install Python dependencies and the pritunl package itself
RUN pip install --break-system-packages -r requirements.txt && \
    pip install --break-system-packages -e .

# Create required directories and non-root user
# OpenVPN requires specific permissions for TUN device
RUN mkdir -p /var/lib/pritunl /var/log/pritunl /etc/pritunl && \
    groupadd -r pritunl && \
    useradd -r -g pritunl -d /var/lib/pritunl -s /usr/sbin/nologin pritunl && \
    chown -R pritunl:pritunl /var/lib/pritunl /var/log/pritunl && \
    cp data/etc/pritunl.conf /etc/pritunl.conf && \
    chown pritunl:pritunl /etc/pritunl.conf && \
    chmod +x /usr/local/bin/docker-entrypoint.sh

# Set ownership for application files
RUN chown -R pritunl:pritunl /app

# Switch to non-root user
USER pritunl

# Exposed ports:
#   443/tcp  - HTTPS web UI and API
#   1194/udp - OpenVPN (UDP mode)
#   1194/tcp - OpenVPN (TCP mode)
EXPOSE 443 1194/udp 1194/tcp

# Health check: verify the web UI is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f -k https://localhost:443/ || exit 1

# Default configuration file path
ENV PRITUNL_CONF=/etc/pritunl.conf

# Entrypoint handles MongoDB URI configuration, then starts pritunl
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command: start the Pritunl daemon
# The daemon will automatically spawn pritunl-web as a subprocess
CMD ["pritunl", "start"]
