#!/usr/bin/env bash
# Start AI Course Advisor: Flask API (port 5000) + Vite (port 5173).
# Prerequisites: PostgreSQL running and DATABASE_URL pointing at your DB if not using the default.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV_PY="$BACKEND/venv/bin/python"
VENV_PIP="$BACKEND/venv/bin/pip"
VENV_FLASK="$BACKEND/venv/bin/flask"

INSTALL=0
MIGRATE=0
SEED=0

usage() {
  cat <<'EOF'
Usage: ./run.sh [OPTIONS]

Starts the Flask backend (http://localhost:5000) and Vite dev server (http://localhost:5173).
Open http://localhost:5173 — the frontend proxies /api to the backend.

OPTIONS
  --install    Create backend/venv, pip install -r requirements.txt, npm install
  --migrate    Run "flask db upgrade" before starting servers (needs venv + DB)
  --seed       Run python seed.py before starting servers (courses, demo user, synthetic data)
  -h, --help   Show this help

PostgreSQL must be reachable (default URI: postgresql://localhost/course_advisor — see README).
First-time setup typically: ./run.sh --install && ./run.sh --migrate --seed
Then: ./run.sh
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install) INSTALL=1 ;;
    --migrate) MIGRATE=1 ;;
    --seed) SEED=1 ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

detect_python() {
  if [[ -x "$VENV_PY" ]]; then
    PYTHON_CREATE="$VENV_PY"
    return
  fi
  if command -v python3.12 &>/dev/null; then PYTHON_CREATE="$(command -v python3.12)"
  elif command -v python3 &>/dev/null; then PYTHON_CREATE="$(command -v python3)"
  elif command -v python &>/dev/null; then PYTHON_CREATE="$(command -v python)"
  fi
}

if [[ "$INSTALL" -eq 1 ]]; then
  detect_python
  if [[ -z "${PYTHON_CREATE:-}" ]]; then
    echo "No Python interpreter found (need python3.12, python3, or python)." >&2
    exit 1
  fi
  echo "Creating venv with: $PYTHON_CREATE"
  "$PYTHON_CREATE" -m venv "$BACKEND/venv"
  "$VENV_PIP" install -r "$BACKEND/requirements.txt"
  (cd "$FRONTEND" && npm install)
fi

if [[ ! -x "$VENV_PY" ]]; then
  echo "Backend venv not found. Run once: ./run.sh --install" >&2
  exit 1
fi

run_backend_cmd() {
  (cd "$BACKEND" && "$@")
}

if [[ "$MIGRATE" -eq 1 ]]; then
  export FLASK_APP=app
  echo "Running database migrations..."
  run_backend_cmd "$VENV_FLASK" db upgrade
fi

if [[ "$SEED" -eq 1 ]]; then
  echo "Seeding database..."
  run_backend_cmd "$VENV_PY" seed.py
fi

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

run_backend_cmd "$VENV_PY" app.py &
BACKEND_PID=$!

echo "Backend PID $BACKEND_PID (http://localhost:5000)"
echo "Starting frontend (http://localhost:5173) — Ctrl+C stops both."

(cd "$FRONTEND" && npm run dev)
cleanup
