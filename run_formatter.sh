#!/usr/bin/env bash
#
# format.sh
#
# This script formats the Python code in the project directory using
# the standard 'isort' and 'black' tools.
#
# It is intended to be run from the root of the project.
# The script will exit immediately if any command fails.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Running isort to sort imports..."
poetry run isort .

echo "Running black for code formatting..."
poetry run black .

echo "--- Formatting complete! ---"
