#!/usr/bin/env bash
#
# This script check the Python code in the project directory using
# the standard 'isort' and 'black' tools.
#
set -e

echo "Running isort checking imports..."
poetry run isort . --check

echo "Running black checking formatting..."
poetry run black . --check

echo "Running Static Analysis..."
poetry run mypy .

