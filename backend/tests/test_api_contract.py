from app.main import app


def test_public_api_routes_match_documented_contract() -> None:
    paths = app.openapi()["paths"]
    routes = {(path, method.upper()) for path, operations in paths.items() for method in operations}

    assert {
        ("/health/live", "GET"),
        ("/health/ready", "GET"),
        ("/api/v1/documents", "GET"),
        ("/api/v1/documents", "POST"),
        ("/api/v1/documents/{document_id}", "DELETE"),
        ("/api/v1/provider/check", "POST"),
        ("/api/v1/chat/ask", "POST"),
    }.issubset(routes)


def test_openapi_endpoints_are_enabled() -> None:
    assert app.docs_url == "/docs"
    assert app.openapi_url == "/openapi.json"
