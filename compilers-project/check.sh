#!/bin/bash
set -euo pipefail
cd "$(dirname "${0}")"
poetry run mypy .
rm -Rf test_programs/workdir
# poetry run pytest -vv tests/

# Check if a specific test file was provided as an argument
if [ "$#" -eq 1 ]; then
    TEST_FILE=$1
    echo "Running specified test file: $TEST_FILE"
    poetry run pytest -vv tests/$TEST_FILE
else
    echo "Running all tests"
    poetry run pytest -vv tests/
fi
