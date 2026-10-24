#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
export AWS_EC2_METADATA_DISABLED=true
exec .venv/bin/python scripts/preflight.py "$@"
