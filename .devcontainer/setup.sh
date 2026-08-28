#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(git rev-parse --show-toplevel)"

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

# Keep generated demo configuration compatible when an existing Codespace resumes.
if grep -q '^GEMINI_MODEL=gemini-2.5-flash-lite$' .env; then
  sed -i 's/^GEMINI_MODEL=gemini-2.5-flash-lite$/GEMINI_MODEL=gemini-3.1-flash-lite/' .env
fi

echo "Building the RAG Explorer services. The local embedding image can take a few minutes on first use..."
docker compose build
docker compose up -d

echo
echo "Setup is complete. When you are ready to view the application, run:"
echo "  bash .devcontainer/print-url.sh"
echo
echo "The page is intentionally not opened automatically so you control when the terminal and port are ready."
