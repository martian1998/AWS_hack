import pytest
from fastapi.testclient import TestClient
from tether.api import app
from tether.worker import handler

client = TestClient(app)
routes = [(method.upper(), path) for path, operations in app.openapi()["paths"].items()
          for method in operations if path != "/health"]


def test_health_exposes_no_configuration_or_docs():
    assert len(routes) == 15, "All protected contract operations must be exercised; never skip an empty route list."
    assert client.get("/health").json() == {"ok": True}
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


@pytest.mark.parametrize("method,path", routes)
def test_every_application_route_rejects_missing_identity(method, path):
    response = client.request(method, path)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"


@pytest.mark.parametrize("method,path", routes)
def test_arbitrary_bearer_never_activates_scaffold_or_accepts_work(method, path):
    response = client.request(method, path, headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "AUTH_NOT_CONFIGURED"
    assert "not-a-real-token" not in response.text


def test_inert_worker_does_not_delete_unimplemented_work():
    result = handler({"Records": [{"messageId":"first"}, {"messageId":"second"}]}, None)
    assert result == {"batchItemFailures": [{"itemIdentifier":"first"}, {"itemIdentifier":"second"}]}
