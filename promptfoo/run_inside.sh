#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
work=${RADAR_EVAL_WORK_DIR:-/tmp}
python3 "$root/promptfoo/network_check.py"
python3 "$root/promptfoo/generate.py"
set +e
node "$root/node_modules/promptfoo/dist/src/main.js" eval -c "$work/promptfoo-config.json" --no-cache --no-share --no-progress-bar --no-table --max-concurrency 1 -o "$work/promptfoo-results.json"
status=$?
set -e
# Promptfoo usa 100 para falhas de asserção. Não aceitar falha operacional.
if [ "$status" -ne 0 ] && [ "$status" -ne 100 ]; then exit "$status"; fi
python3 "$root/promptfoo/verify.py"
