#!/usr/bin/env bash
# Source from repository scripts. Does not load credential files or change global tools.
TETHER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -x "$TETHER_ROOT/.tools/node/node_modules/node/bin/node" ]; then
  export PATH="$TETHER_ROOT/.tools/node/node_modules/node/bin:$PATH"
fi
export SAM_CLI_TELEMETRY=0
export __SAM_CLI_APP_DIR="$TETHER_ROOT/.cache/sam"
export npm_config_cache="$TETHER_ROOT/.cache/npm"
cd "$TETHER_ROOT"
