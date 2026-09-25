from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.database import HistoryRepository, get_history_repository
from app.main import app


@pytest.fixture
def repository(tmp_path: Path) -> HistoryRepository:
    history_repository = HistoryRepository(tmp_path / "calculator.db")
    history_repository.initialize()
    return history_repository


@pytest.fixture
def client(repository: HistoryRepository):
    app.dependency_overrides[get_history_repository] = lambda: repository
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_calculate_returns_result_and_stores_history(
    client: TestClient,
    repository: HistoryRepository,
) -> None:
    response = client.post("/api/calculate", json={"expression": "(1+2)*3"})

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["error"] is None
    assert body["data"]["expression"] == "(1+2)*3"
    assert body["data"]["result"] == "9"
    assert body["data"]["id"] == 1
    assert body["data"]["created_at"]

    history = repository.query_all()
    assert len(history) == 1
    assert history[0].expression == "(1+2)*3"
    assert history[0].result == "9"


def test_invalid_expression_returns_400_without_storing_history(
    client: TestClient,
    repository: HistoryRepository,
) -> None:
    response = client.post("/api/calculate", json={"expression": "1 + * 2"})

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "data": None,
        "error": {
            "code": "INVALID_EXPRESSION",
            "message": "The expression is invalid",
        },
    }
    assert repository.query_all() == []


def test_division_by_zero_returns_422_without_storing_history(
    client: TestClient,
    repository: HistoryRepository,
) -> None:
    response = client.post("/api/calculate", json={"expression": "10 / 0"})

    assert response.status_code == 422
    assert response.json()["error"] == {
        "code": "DIVISION_BY_ZERO",
        "message": "Division by zero is not allowed",
    }
    assert repository.query_all() == []


@pytest.mark.parametrize("payload", [{}, {"expression": None}, {"expression": 12}])
def test_invalid_request_uses_unified_response(
    client: TestClient,
    repository: HistoryRepository,
    payload: dict[str, object],
) -> None:
    response = client.post("/api/calculate", json=payload)

    assert response.status_code == 422
    assert response.json() == {
        "success": False,
        "data": None,
        "error": {
            "code": "INVALID_REQUEST",
            "message": "The request data is invalid",
        },
    }
    assert repository.query_all() == []


def test_internal_error_does_not_leak_exception_details(
    repository: HistoryRepository,
) -> None:
    class FailingRepository:
        def insert(self, *args, **kwargs):
            raise RuntimeError("private database password and stack details")

    app.dependency_overrides[get_history_repository] = lambda: FailingRepository()
    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.post("/api/calculate", json={"expression": "1 + 2"})
    app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "data": None,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An internal server error occurred",
        },
    }
    assert "password" not in response.text
    assert "RuntimeError" not in response.text
    assert repository.query_all() == []
