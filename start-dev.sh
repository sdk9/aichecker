#!/usr/bin/env bash
# VeritasAI — development startup script
set -e

echo "╔══════════════════════════════════════╗"
echo "║       VeritasAI Dev Server           ║"
echo "╚══════════════════════════════════════╝"

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found"
  exit 1
fi

# Check Node
if ! command -v node &>/dev/null; then
  echo "ERROR: node not found"
  exit 1
fi

# ── Backend setup ──
echo ""
echo "▶ Setting up Python backend..."
cd "$(dirname "$0")/backend"

if [ ! -d ".venv" ]; then
  echo "  Creating virtualenv..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "  Installing Python deps..."
pip install -q -r requirements.txt

echo "  Starting FastAPI on http://localhost:8000 ..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ..

# ── Frontend setup ──
echo ""
echo "▶ Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
  echo "  Installing npm deps..."
  npm install
fi

echo "  Starting Vite on http://localhost:5173 ..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  VeritasAI is running!                       ║"
echo "║                                              ║"
echo "║  Frontend:  http://localhost:5173            ║"
echo "║  Backend:   http://localhost:8000            ║"
echo "║  API Docs:  http://localhost:8000/api/docs   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop both servers."

# Wait for either to exit, then kill both
wait_and_cleanup() {
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit 0
}
trap wait_and_cleanup INT TERM

wait
