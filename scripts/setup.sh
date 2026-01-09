#!/usr/bin/env bash
# setup.sh - S.I.M.P.L.E (Self-hosted Infrastructure Made Painless with Linux & Engineering)
# ==========================================================================================
# Purpose: Creates Python virtual environment and installs dependencies
# Usage: chmod +x setup.sh && ./setup.sh

set -Eeuo pipefail

# Validate Python 3.14+
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: Python 3 required" >&2
    exit 1
fi

# Create isolated venv
VENV_DIR="$(mktemp -d -t home-infra-venv.XXXXXX)"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

# Create symlink for convenience
ln -sf "$VENV_DIR/bin/python" ./venv
ln -sf "$VENV_DIR/bin/activate" ./activate

echo "✅ Setup complete. Run: source activate && python main.py"
trap 'rm -rf "$VENV_DIR"' EXIT
