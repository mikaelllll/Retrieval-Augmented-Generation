#!/usr/bin/env bash
set -Eeuo pipefail

if [[ -n "${CODESPACE_NAME:-}" && -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]]; then
  url="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
else
  url="http://localhost:3000"
fi

echo
echo "RAG Explorer frontend:"
echo "  ${url}"
echo
echo "If the URL does not open, use the Codespaces Ports tab, find port 3000, and select Open in Browser."

