#!/usr/bin/env bash
# Installazione Scout su macOS / Linux.
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip >/dev/null
.venv/bin/python -m pip install -r requirements.txt
mkdir -p ../prospect
echo
echo "Fatto. Prova con:"
echo "  .venv/bin/python scout.py tutto --comune Vigevano -o ../prospect/vigevano.csv"
