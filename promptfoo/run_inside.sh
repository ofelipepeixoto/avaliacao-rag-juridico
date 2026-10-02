#!/bin/sh
set -eu
python3 /lab/promptfoo/network_check.py
python3 /lab/promptfoo/generate.py
set +e
node /lab/node_modules/promptfoo/dist/src/main.js eval -c /tmp/promptfoo-config.json --no-cache --no-share --no-progress-bar --no-table --max-concurrency 1 -o /tmp/promptfoo-results.json
status=$?
set -e
# Promptfoo usa 100 para falhas de asserção. Não aceitar falha operacional.
if [ "$status" -ne 0 ] && [ "$status" -ne 100 ]; then exit "$status"; fi
python3 /lab/promptfoo/verify.py
