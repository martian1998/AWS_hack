#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
if [ "${1:-local}" != local ]; then
  printf '%s\n' 'BLOCKED: deployed smoke tests require Stage B and a verified API URL.' >&2
  exit 2
fi
.venv/bin/python -m pytest tests/test_api.py
