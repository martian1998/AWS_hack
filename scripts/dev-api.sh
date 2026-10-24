#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
exec .venv/bin/python -m uvicorn tether.api:app --app-dir backend --host 127.0.0.1 --port 8000
