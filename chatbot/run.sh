#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ ! -d .venv-chatbot ]]; then
  python3 -m venv .venv-chatbot
  . .venv-chatbot/bin/activate
  pip install -q -r chatbot/requirements.txt
else
  . .venv-chatbot/bin/activate
fi
exec python chatbot/app.py
