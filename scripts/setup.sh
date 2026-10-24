#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
TETHER_PYTHON="${TETHER_PYTHON:-python3.14}"
"$TETHER_PYTHON" -c 'import sys; assert sys.version_info[:2] == (3,14), "Use Python 3.14"'
node -e 'if (process.versions.node.split(".")[0] !== "24") throw new Error("Use Node 24 LTS; see SETUP.md")'
"$TETHER_PYTHON" -m venv .venv
.venv/bin/python -m pip install --cache-dir .cache/pip -r requirements-dev.lock
npm --prefix frontend ci
./scripts/contracts.sh
./scripts/seed.sh
