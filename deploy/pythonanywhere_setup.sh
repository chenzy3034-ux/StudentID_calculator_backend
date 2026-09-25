#!/usr/bin/env bash

set -euo pipefail

APP_ROOT="$HOME/StudentID_calculator_backend"
VENV_ROOT="$HOME/.virtualenvs/calculator-backend"
DATABASE_PATH="$APP_ROOT/data/calculator.db"
FRONTEND_ORIGIN="https://chenzy3034-ux.github.io"
DOMAIN="chenzy.pythonanywhere.com"

python3.10 -m venv "$VENV_ROOT"
"$VENV_ROOT/bin/python" -m pip install --upgrade pip
"$VENV_ROOT/bin/python" -m pip install -r "$APP_ROOT/requirements.txt"
python3.10 -m pip install --user --upgrade pythonanywhere
mkdir -p "$APP_ROOT/data"

WEBSITE_COMMAND="/usr/bin/env CALCULATOR_DATABASE_PATH=$DATABASE_PATH CALCULATOR_CORS_ORIGINS=$FRONTEND_ORIGIN $VENV_ROOT/bin/uvicorn --app-dir $APP_ROOT --uds \${DOMAIN_SOCKET} app.main:app"

"$HOME/.local/bin/pa" website create \
  --domain "$DOMAIN" \
  --command "$WEBSITE_COMMAND"

echo "Backend deployed at https://$DOMAIN"
