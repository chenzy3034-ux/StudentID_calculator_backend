# 832401306 Calculator Backend

## Project introduction

This repository contains the API and persistence layer for a front-end/back-end
separation calculator system. The backend validates and evaluates arithmetic
expressions, stores every successful calculation in SQLite, returns calculation
history, and deletes individual history records.

All final calculations happen in this service. Expression text is processed by
a restricted tokenizer, recursive-descent parser, and `Decimal` evaluator. The
project does not use `eval`, `exec`, `compile`, or another mechanism that
executes user input as Python code.

## Public deployment

- Backend API: `https://chenzy.pythonanywhere.com`
- Health check: `https://chenzy.pythonanywhere.com/health`
- Frontend: `https://chenzy3034-ux.github.io/832401306_calculator_frontend/`

The backend is deployed on the free PythonAnywhere plan as an ASGI website. Its
SQLite database is stored at
`/home/Chenzy/832401306_calculator_backend/data/calculator.db`, which is inside
the account's persistent home storage and remains available across application
reloads.

## Technology stack

- Python 3.12
- FastAPI
- Uvicorn
- SQLite through Python's standard `sqlite3` module
- Pydantic
- pytest and HTTPX for tests

## Runtime environment

- Python `3.12` is recommended
- `pip`
- A terminal capable of activating a Python virtual environment

The project was developed and verified on macOS with Apple Silicon using Python
`3.12.4`. The commands below are for macOS and Linux. On Windows, use the
equivalent virtual-environment activation command.

Check the Python version:

```sh
python3 --version
```

## Installation and virtual environment

Run all commands in this repository's root directory:

```sh
cd 832401306_calculator_backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The `.venv` directory is ignored by Git and belongs only to this local checkout.
Activate it again in every new terminal session. To leave the virtual
environment, run `deactivate`.

For development and tests, install the additional dependencies instead:

```sh
python -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` includes the runtime requirements, so it may be used on
its own in a development environment.

## Configuration

Both settings are optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `CALCULATOR_DATABASE_PATH` | `data/calculator.db` | SQLite database file path |
| `CALCULATOR_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated frontend origins allowed by CORS |

Example for a shell session:

```sh
export CALCULATOR_DATABASE_PATH="$PWD/data/calculator.db"
export CALCULATOR_CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
```

Each CORS entry must be an origin consisting of scheme, host, and optional port;
do not include a path such as `/api`. Set these variables before starting
Uvicorn. A relative database path is resolved from the directory where Uvicorn
is started, so an absolute path is preferable when overriding the default.

## Database initialization

No separate database server or manual SQL command is required. When FastAPI
starts, its lifespan handler automatically:

1. creates the parent directory for the configured SQLite file;
2. creates the SQLite file if it does not exist; and
3. creates the `calculation_history` table with `id`, `expression`, `result`,
   and `created_at` columns if the table does not exist.

With the default configuration, the persistent file is:

```text
data/calculator.db
```

The `data/` directory and database files are ignored by Git. Do not delete the
database file if its saved history must be retained. Restarting the backend does
not remove history.

## Startup

Activate the virtual environment and start the API from the repository root:

```sh
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Useful local URLs:

- Health check: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

Verify startup in another terminal:

```sh
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Stop the server with `Control-C`.

## PythonAnywhere deployment

The account must have an API token generated from **Account > API token**.
PythonAnywhere makes that token available to commands running in its own Bash
consoles, so the token must not be copied into this repository.

For a first deployment, open a fresh PythonAnywhere Bash console and run:

```sh
git clone https://github.com/chenzy3034-ux/832401306_calculator_backend.git
bash "$HOME/832401306_calculator_backend/deploy/pythonanywhere_setup.sh"
```

The script creates a Python 3.10 virtual environment, installs the runtime
dependencies, creates the persistent data directory, installs PythonAnywhere's
official `pa` command, and creates the ASGI website. The stored Uvicorn command
sets these production values:

```text
CALCULATOR_DATABASE_PATH=/home/Chenzy/832401306_calculator_backend/data/calculator.db
CALCULATOR_CORS_ORIGINS=https://chenzy3034-ux.github.io
```

After later code updates, run the following in a PythonAnywhere Bash console:

```sh
cd "$HOME/832401306_calculator_backend"
git pull
"$HOME/.local/bin/pa" website reload --domain chenzy.pythonanywhere.com
```

PythonAnywhere serves the account subdomain over HTTPS. The free plan has CPU,
storage, and outbound-network limits suitable for this assignment's light
grading traffic. The ASGI hosting interface is currently described by
PythonAnywhere as beta, so use the `pa website get` command and the logs under
`/var/log/chenzy.pythonanywhere.com.*.log` when diagnosing deployment issues.

## API endpoints

### Calculate and save an expression

`POST /api/calculate`

Request:

```json
{
  "expression": "(1+2)*3"
}
```

Successful calculation: HTTP `201 Created`. The returned record has already
been saved to SQLite.

```json
{
  "success": true,
  "data": {
    "id": 1,
    "expression": "(1+2)*3",
    "result": "9",
    "created_at": "2026-09-25T10:00:00+00:00"
  },
  "error": null
}
```

Supported expressions include `+`, `-`, `*`, `/`, operator precedence,
parentheses, unary plus and minus, and decimal numbers. Invalid expressions
return HTTP `400`; division by zero returns HTTP `422`. Failed calculations are
not stored.

Example request:

```sh
curl -X POST http://127.0.0.1:8000/api/calculate \
  -H 'Content-Type: application/json' \
  -d '{"expression":"(1+2)*3"}'
```

### List calculation history

`GET /api/history`

Successful request: HTTP `200 OK`. Records are returned newest first. Each item
contains `id`, `expression`, `result`, and `created_at`.

```sh
curl http://127.0.0.1:8000/api/history
```

### Delete one history record

`DELETE /api/history/{id}`

Successful deletion: HTTP `200 OK`. A missing ID returns HTTP `404`.

```sh
curl -X DELETE http://127.0.0.1:8000/api/history/1
```

All application API responses use the same top-level fields:

- success: `{"success": true, "data": ..., "error": null}`
- failure: `{"success": false, "data": null, "error": {"code": "...", "message": "..."}}`

Internal Python exception details and stack traces are not returned in API
responses.

## Frontend/backend connection

The frontend defaults to `http://127.0.0.1:8000`. For the standard local setup:

1. start this backend on port `8000`;
2. start the frontend Vite server in a second terminal; and
3. open the frontend URL, normally `http://localhost:5173`.

If the frontend uses another origin, add that exact origin to
`CALCULATOR_CORS_ORIGINS` before starting this service. If the backend uses a
different address, set `VITE_API_BASE_URL` in the frontend repository.

## Tests

Install the development dependencies and run the complete backend test suite:

```sh
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest
```

The test suite covers expression tokenization, parsing and evaluation; invalid
expressions; division by zero; SQLite insertion, querying, persistence and
deletion; calculation API behavior; history API behavior; and failed-request
storage rules.

## Project structure

```text
.
├── app/
│   ├── api/                 # FastAPI routes and response helpers
│   ├── calculator/          # Tokenizer, parser, evaluator, and errors
│   ├── database/            # SQLite connection, schema, model, repository
│   ├── services/            # Calculation and history use cases
│   ├── config.py            # Runtime configuration
│   ├── main.py              # FastAPI application and middleware
│   └── schemas.py           # Request and response schemas
├── tests/                   # Unit, database, and API tests
├── deploy/                  # PythonAnywhere deployment setup
├── codestyle.md             # Project Python style rules
├── requirements.txt         # Runtime dependencies
└── requirements-dev.txt     # Runtime and test dependencies
```

## Run checklist

1. Create and activate `.venv`.
2. Install `requirements-dev.txt` for a development checkout, or
   `requirements.txt` for runtime only.
3. Start Uvicorn from the repository root.
4. Confirm that `/health` returns `{"status":"ok"}`.
5. Start the frontend and calculate `1 + 2`.
6. Refresh the page and confirm the saved record remains in history.

This directory is designed to be maintained as an independent backend GitHub
repository.
