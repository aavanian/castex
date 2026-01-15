#!/bin/bash
set -euo pipefail

echo "=== Running ruff format ==="
uv run ruff format src tests scripts

echo "=== Running ruff check ==="
uv run ruff check --fix src tests scripts

echo "=== Running mypy ==="
uv run mypy src tests scripts

echo "=== Running pytest ==="
uv run pytest -v

echo "=== All checks passed ==="
