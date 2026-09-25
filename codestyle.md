# Backend Code Style

**Source:** This project follows
[PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/).
The rules below select the parts relevant to this FastAPI and SQLite project
and add project-specific architecture and safety requirements.

## Scope and formatting

- Target Python 3.12 or a compatible Python 3 release used by the project.
- Save source files as UTF-8 with LF line endings and a final newline.
- Indent with 4 spaces. Never use tabs for indentation.
- Use a practical maximum line length of 88 characters. Wrap expressions
  inside parentheses instead of using backslashes.
- Put two blank lines around top-level classes and functions, and one blank
  line between logical sections inside a class or function.
- Remove trailing whitespace and keep imports at the top of the file.

## Imports

- Group imports in this order: standard library, third-party packages, local
  application modules. Separate groups with one blank line.
- Prefer one module per `import` statement. Parenthesize long `from ... import`
  lists.
- Use absolute imports beginning with `app` for application code.
- Do not use wildcard imports.

## Naming

- Use `snake_case` for modules, functions, methods, local variables, and
  parameters.
- Use `PascalCase` for classes and exceptions.
- Use `UPPER_SNAKE_CASE` for module-level constants.
- Prefix implementation-only attributes with one underscore.
- Give domain concepts explicit names such as `HistoryRepository` and
  `InvalidExpressionError`; avoid unexplained abbreviations.

## Types, functions, and documentation

- Add type hints to public functions, service boundaries, repository methods,
  and FastAPI dependencies.
- Use built-in generics such as `list[str]` and the `X | None` union syntax.
- Keep functions focused on one responsibility and return predictable types.
- Add concise docstrings to public classes or non-obvious functions. Comments
  explain why a decision exists rather than translating code into prose.
- Catch only exceptions that can be handled meaningfully. Preserve causes with
  `raise ... from error` when translating an exception.

## FastAPI architecture

- API modules handle HTTP concerns: request models, status codes, dependency
  injection, and response models.
- Service modules coordinate use cases such as calculate-then-store. They do
  not contain HTTP response construction or SQL.
- Calculator modules tokenize, parse, and evaluate expressions independently
  of FastAPI and SQLite.
- Database modules own connections, schema creation, SQL, and persistence.
- Pydantic schemas define every public JSON request and response shape.
- Return the shared `success`, `data`, and `error` response structure. Do not
  expose Python exception text or stack traces to clients.

## Calculator and database safety

- Never use `eval`, `exec`, `compile`, subprocesses, or any equivalent method
  to execute user expressions.
- Accept only tokens explicitly supported by the calculator grammar.
- Use `Decimal` for calculator arithmetic and raise domain-specific exceptions
  for invalid expressions and division by zero.
- Persist a calculation only after evaluation succeeds.
- Use parameterized SQL for every value. Never interpolate user data into SQL.
- Use the file-backed SQLite database configured by
  `CALCULATOR_DATABASE_PATH`; do not replace persistence with process memory.
- Keep timestamps timezone-aware and serialize them in ISO 8601 form.

## Tests

- Use pytest and name test files `test_*.py` and test functions `test_*`.
- Cover successful behavior, boundary cases, failure behavior, and the absence
  of unwanted side effects such as saving a failed calculation.
- Use `tmp_path` and dependency overrides so tests do not modify the normal
  application database.
- Verify database persistence by reconnecting to the same SQLite file.
- Test APIs through FastAPI's test client and assert status codes, response
  bodies, and database state.

Before committing backend changes, run:

```sh
python -m pytest
python -m compileall -q app tests
```
