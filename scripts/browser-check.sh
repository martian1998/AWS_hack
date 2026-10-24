#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd frontend
exec ./node_modules/.bin/playwright test
