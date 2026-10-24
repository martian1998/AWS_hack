#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
.venv/bin/python -m pytest
.venv/bin/python scripts/export_contracts.py --check
npm --prefix frontend run contracts:check
npm --prefix frontend run typecheck
npm --prefix frontend test
npm --prefix frontend run build
sam validate --lint --region us-east-1 --template-file infra/template.yaml
