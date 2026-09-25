import os


DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


def get_cors_origins() -> list[str]:
    """Return browser origins allowed to call the backend API."""
    configured_origins = os.getenv("CALCULATOR_CORS_ORIGINS")
    if configured_origins is None:
        return list(DEFAULT_CORS_ORIGINS)

    return [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]
