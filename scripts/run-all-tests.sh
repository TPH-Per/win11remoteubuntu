#!/usr/bin/env bash
set -e

echo "=== Running Shared Tests ==="
pytest tests/shared/ -v

echo "=== Running Ubuntu Server Tests ==="
cd ubuntu-server
pytest tests/ -v
cd ..

echo "=== Running Windows Client Tests ==="
cd windows-client
pytest tests/ -v
cd ..

echo "=== Running Integration Tests ==="
pytest tests/integration/ -v
