# Operations

## Codespaces lifecycle

`postCreateCommand` copies safe local defaults, builds images, and starts the Compose application. `postStartCommand` restarts existing containers when the Codespace resumes. Port 3000 sends a notification but never forcibly opens a browser.

Print the correct URL after the terminal is available:

```bash
bash .devcontainer/print-url.sh
```

## Useful commands

```bash
docker compose ps
docker compose logs -f api worker
docker compose restart api worker
curl -fsS http://localhost:8000/health/ready
curl -fsS http://localhost:3000/healthz
```

The first document takes longer because the worker downloads and caches the embedding model. Subsequent ingestion reuses the named `model_cache` volume.

## Troubleshooting

- **No terminal output:** accept the repository trust prompt, open a terminal, and run `print-url.sh`.
- **Port is private:** in the Ports tab, right-click 3000 and change visibility if your GitHub policy permits it.
- **Document stays queued:** inspect `docker compose logs worker` and verify Redis health.
- **Gemini returns 429:** wait for the free-tier quota window or use another Google project/key.
- **No extracted text:** the PDF may contain scanned images; OCR is intentionally documented as a future extension.

