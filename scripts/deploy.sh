#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
# Fail before performing any cloud mutation: Stage A has no durable intake.
printf '%s\n' 'BLOCKED: Stage A is an inert foundation, not a deployable patient flow.' 'Implement Stage B and its auth/durability tests, then replace this gate with verified account/profile deployment. See docs/runbook.md.' >&2
exit 2
