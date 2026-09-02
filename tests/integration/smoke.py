"""End-to-end smoke test for a running RAG Explorer Docker Compose stack."""

from __future__ import annotations

import json
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

API_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:3000"


def call(
    method: str,
    url: str,
    *,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    expected: int = 200,
) -> tuple[object | None, dict[str, str]]:
    req = Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urlopen(req, timeout=20) as response:
            status = response.status
            raw = response.read()
            response_headers = {key.lower(): value for key, value in response.headers.items()}
    except HTTPError as exc:
        status = exc.code
        raw = exc.read()
        response_headers = {key.lower(): value for key, value in exc.headers.items()}

    assert status == expected, f"{method} {url}: expected {expected}, got {status}: {raw!r}"
    content_type = response_headers.get("content-type", "")
    parsed = json.loads(raw) if raw and "json" in content_type else raw.decode()
    return parsed, response_headers


def multipart_pdf(filename: str, content: bytes) -> tuple[bytes, str]:
    boundary = f"----rag-integration-{uuid.uuid4().hex}"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: application/pdf\r\n\r\n"
    ).encode() + content + f"\r\n--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


def main() -> None:
    ready, _ = call("GET", API_URL + "/health/ready")
    assert ready == {"status": "ready"}
    frontend_health, _ = call("GET", FRONTEND_URL + "/healthz")
    assert frontend_health == "ok"

    workspace = str(uuid.uuid4())
    other_workspace = str(uuid.uuid4())
    workspace_headers = {"X-Workspace-ID": workspace}

    documents, _ = call(
        "GET",
        FRONTEND_URL + "/api/v1/documents",
        headers=workspace_headers,
    )
    assert documents == []

    invalid_body = b"not a pdf"
    boundary = f"----rag-invalid-{uuid.uuid4().hex}"
    invalid_multipart = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="notes.txt"\r\n'
        "Content-Type: text/plain\r\n\r\n"
    ).encode() + invalid_body + f"\r\n--{boundary}--\r\n".encode()
    call(
        "POST",
        API_URL + "/api/v1/documents",
        body=invalid_multipart,
        headers={
            **workspace_headers,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        expected=415,
    )

    pdf_body, content_type = multipart_pdf("integration.pdf", b"%PDF-1.4\n%%EOF\n")
    created, _ = call(
        "POST",
        API_URL + "/api/v1/documents",
        body=pdf_body,
        headers={**workspace_headers, "Content-Type": content_type},
        expected=202,
    )
    assert isinstance(created, dict)
    assert created["filename"] == "integration.pdf"
    document_id = created["id"]

    visible, _ = call(
        "GET",
        API_URL + "/api/v1/documents",
        headers=workspace_headers,
    )
    assert isinstance(visible, list) and any(item["id"] == document_id for item in visible)

    isolated, _ = call(
        "GET",
        API_URL + "/api/v1/documents",
        headers={"X-Workspace-ID": other_workspace},
    )
    assert isolated == []

    call(
        "DELETE",
        API_URL + f"/api/v1/documents/{document_id}",
        headers=workspace_headers,
        expected=204,
    )
    remaining, _ = call(
        "GET",
        API_URL + "/api/v1/documents",
        headers=workspace_headers,
    )
    assert remaining == []

    print("RAG Explorer live-stack integration test passed")


if __name__ == "__main__":
    main()
