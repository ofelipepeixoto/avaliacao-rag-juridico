#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
# Instalação npm ci e pull da imagem ocorrem ANTES da avaliação isolada.
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --user "$(id -u):$(id -g)" --memory 2g --cpus 2 --pids-limit 128 \
  --tmpfs /tmp:rw,nosuid,nodev,size=256m \
  -e HOME=/tmp -e PROMPTFOO_CONFIG_DIR=/tmp/promptfoo \
  -e PROMPTFOO_DISABLE_TELEMETRY=1 -e PROMPTFOO_DISABLE_UPDATE=1 \
  -e PROMPTFOO_DISABLE_SHARING=1 -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$PWD:/lab:ro" -w /lab \
  node@sha256:64af3819f9275802414d7cdc38c27e9d82bd564dec4d4da87d008255d36c63b4 \
  sh /lab/promptfoo/run_inside.sh
