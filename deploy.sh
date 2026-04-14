#!/usr/bin/env bash
# VeritasAI — VPS deployment script
# Run this on the VPS as root after SSH-ing in: ssh root@2.24.28.22
set -e

echo "=== VeritasAI VPS Deployment ==="

# ── 1. Install Docker if not present ──────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "[1/6] Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  systemctl enable docker
  systemctl start docker
else
  echo "[1/6] Docker already installed: $(docker --version)"
fi

# ── 2. Install docker compose plugin if not present ───────────────────────────
if ! docker compose version &>/dev/null; then
  echo "[2/6] Installing Docker Compose plugin..."
  apt-get install -y docker-compose-plugin 2>/dev/null || \
    curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
      -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose
else
  echo "[2/6] Docker Compose already installed"
fi

# ── 3. Clone / pull repo ──────────────────────────────────────────────────────
echo "[3/6] Pulling repository..."
if [ -d /opt/aichecker ]; then
  cd /opt/aichecker && git pull origin main
else
  git clone https://github.com/sdk9/aichecker.git /opt/aichecker
  cd /opt/aichecker
fi

# ── 4. Create .env if it doesn't exist ────────────────────────────────────────
echo "[4/6] Checking .env..."
if [ ! -f /opt/aichecker/.env ]; then
  cp /opt/aichecker/.env.example /opt/aichecker/.env
  # Auto-generate SECRET_KEY
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  sed -i "s/your-secret-key-here/$SECRET/" /opt/aichecker/.env
  echo ""
  echo "  ⚠  .env created with a random SECRET_KEY."
  echo "  Edit /opt/aichecker/.env to add your Stripe keys and SMTP settings:"
  echo "    nano /opt/aichecker/.env"
  echo ""
fi

# ── 5. Build and start containers ─────────────────────────────────────────────
echo "[5/6] Building and starting containers (this takes ~5 min first time)..."
cd /opt/aichecker
docker compose pull 2>/dev/null || true
docker compose up -d --build

# ── 6. Health check ───────────────────────────────────────────────────────────
echo "[6/6] Waiting for backend health check..."
for i in $(seq 1 24); do
  if curl -sf http://localhost:8000/api/health >/dev/null 2>&1; then
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "  Frontend: http://2.24.28.22:3000"
    echo "  Backend:  http://2.24.28.22:8000"
    echo "  API docs: http://2.24.28.22:8000/api/docs"
    echo ""
    echo "Next steps:"
    echo "  1. Edit /opt/aichecker/.env with your Stripe keys"
    echo "  2. Run: cd /opt/aichecker && docker compose up -d"
    echo "  3. To view logs: docker compose logs -f"
    exit 0
  fi
  echo "  Waiting... ($i/24)"
  sleep 5
done

echo "⚠  Health check timed out. Check logs: cd /opt/aichecker && docker compose logs backend"
