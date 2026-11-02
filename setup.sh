#!/usr/bin/env bash
# Installazione degli agent su macOS / Linux: un solo ambiente .venv per tutti.
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip >/dev/null
.venv/bin/python -m pip install -r requirements.txt
mkdir -p prospect clienti
rm -rf scout/.venv
echo
echo "Fatto. Prova con:"
echo "  .venv/bin/python scout/scout.py tutto --comune Vigevano -o prospect/vigevano.csv"
echo "  .venv/bin/python analista/analista.py analizza www.sito-azienda.it"
