# Security

## Implemented controls

- No application-owned Gemini secret exists; users bring a session-only key.
- Keys are accepted in a header, excluded from models, database writes, Redis values, and logs.
- Generated UUID paths prevent user-controlled filenames from selecting storage locations.
- PDF extension, MIME, size, and magic bytes are validated.
- Retrieval and mutations require the same workspace ID that owns the document.
- The model receives no database or filesystem tool.
- Prompts explicitly treat retrieved documents as untrusted data to reduce indirect prompt injection.
- Nginx applies a body-size limit and baseline browser security headers.
- Containers use fixed major/minor image families, health checks, and isolated Compose networking.
- CI receives read-only repository permissions and contains no deployment secret.

## Honest limitations

The workspace ID is convenience isolation, not authentication. Anyone who obtains it can impersonate that workspace. The demo also lacks malware scanning, encrypted object storage, audit retention, per-user rate limiting, and formal deletion guarantees. Free-tier Gemini may process data under terms unsuitable for confidential material.

A production version should use OAuth/OIDC sessions, server-side authorization, a secrets manager, explicit retention policies, antivirus scanning, rate limits, audit events, TLS at every hop, content-security policy tailored to self-hosted assets, and automated dependency/image scanning.

