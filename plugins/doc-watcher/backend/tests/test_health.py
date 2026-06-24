from fastapi.testclient import TestClient

from app.main import app, create_app


def route_paths(target_app):
    return {getattr(route, "path", "") for route in target_app.router.routes}


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_default_app_exposes_only_audit_api_surface():
    paths = route_paths(app)

    assert "/api/v1/audit/status" in paths
    assert "/api/v1/projects" not in paths
    assert "/api/v1/webhooks/gitea" not in paths


def test_legacy_routes_are_explicitly_opted_in():
    legacy_app = create_app(include_legacy_routes=True)
    paths = route_paths(legacy_app)

    assert "/api/v1/audit/status" in paths
    assert "/api/v1/projects" in paths
    assert "/api/v1/webhooks/gitea" in paths
