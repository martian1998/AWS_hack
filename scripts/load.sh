#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'BLOCKED: rate-controlled load requires Stage B durable intake and Stage D shared admission caps. No load test has run.' >&2
exit 2
