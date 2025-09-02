#!/usr/bin/env bash
set -euo pipefail

echo "Running preflight checks..."

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$ROOT_DIR/data"

# Check data files
H5_FILE="$DATA_DIR/base_simulation.hdf5"
CSV_FILE="$DATA_DIR/asset_categories.csv"

if [[ -f "$H5_FILE" ]]; then
  echo "[OK] Found $H5_FILE"
else
  echo "[WARN] Missing $H5_FILE"
fi

if [[ -f "$CSV_FILE" ]]; then
  echo "[OK] Found $CSV_FILE"
else
  echo "[WARN] Missing $CSV_FILE"
fi

# Port 8000 availability
if lsof -i :8000 >/dev/null 2>&1; then
  echo "[WARN] Port 8000 is in use"
else
  echo "[OK] Port 8000 is available."
fi

# Backend venv
if [[ -d "$ROOT_DIR/backend/.venv" ]]; then
  echo "[OK] Backend venv exists."
else
  echo "[WARN] Backend venv missing. Run: make install-backend"
fi

echo "Preflight checks completed."


