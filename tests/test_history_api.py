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


def test_get_history_reads_records_from_sqlite(
    client: TestClient,
    repository: HistoryRepository,
) -> None:
    older = repository.insert(
        "1 + 2",
        "3",
        created_at="2026-09-25T01:00:00+00:00",
    )
    newer = repository.insert(
        "4 * 5",
        "20",
        created_at="2026-09-25T02:00:00+00:00",
    )

    response = client.get("/api/history")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": [
            {
                "id": newer.id,
                "expression": "4 * 5",
                "result": "20",
                "created_at": "2026-09-25T02:00:00+00:00",
            },
            {
                "id": older.id,
                "expression": "1 + 2",
                "result": "3",
                "created_at": "2026-09-25T01:00:00+00:00",
            },
        ],
        "error": None,
    }


def test_get_history_returns_empty_list(client: TestClient) -> None:
    response = client.get("/api/history")

    assert response.status_code == 200
    assert response.json() == {"success": True, "data": [], "error": None}


def test_delete_history_removes_database_record(
    client: TestClient,
    repository: HistoryRepository,
) -> None:
    retained = repository.insert("1 + 2", "3")
    deleted = repository.insert("10 / 2", "5")

    response = client.delete(f"/api/history/{deleted.id}")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"id": deleted.id},
        "error": None,
    }
    assert repository.query_all() == [retained]

    refreshed_history = client.get("/api/history").json()["data"]
    assert [record["id"] for record in refreshed_history] == [retained.id]


def test_delete_nonexistent_history_returns_404(
    client: TestClient,
    repository: HistoryRepository,
) -> None:
    response = client.delete("/api/history/999")

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "data": None,
        "error": {
            "code": "HISTORY_NOT_FOUND",
            "message": "The calculation history record was not found",
        },
    }
    assert repository.query_all() == []


def test_delete_with_invalid_id_uses_generic_validation_response(
    client: TestClient,
) -> None:
    response = client.delete("/api/history/not-an-integer")

    assert response.status_code == 422
    assert response.json() == {
        "success": False,
        "data": None,
        "error": {
            "code": "INVALID_REQUEST",
            "message": "The request data is invalid",
        },
    }


def test_local_frontend_origin_is_allowed(client: TestClient) -> None:
    response = client.options(
        "/api/calculate",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_calculation_history_api_lifecycle(client: TestClient) -> None:
    calculation_response = client.post(
        "/api/calculate",
        json={"expression": "1 + 2 * 3"},
    )
    history_id = calculation_response.json()["data"]["id"]

    history_response = client.get("/api/history")
    delete_response = client.delete(f"/api/history/{history_id}")
    empty_history_response = client.get("/api/history")

    assert calculation_response.status_code == 201
    assert history_response.status_code == 200
    assert history_response.json()["data"][0]["result"] == "7"
    assert delete_response.status_code == 200
    assert empty_history_response.json()["data"] == []
