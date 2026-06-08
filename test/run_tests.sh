#!/usr/bin/env bash
# Run the Jarvis test suite. No external deps — uses stdlib unittest.
set -e

cd "$(dirname "$0")/.."

echo "==> Running Jarvis tests"
python3 -m unittest discover -s test -p "test_*.py" -v
echo "==> All tests passed."
