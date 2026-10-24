#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'BLOCKED: no original labeled gold set or live triage adapter. See eval/README.md. No evaluation has run.' >&2
exit 2
