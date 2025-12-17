#!/bin/bash
# Run all tests with coverage

echo "Running unit tests with coverage..."

# Run tests with coverage
python -m coverage run -m unittest discover -s . -p "test_*.py" -v

# Generate coverage report
echo -e "\n=== Coverage Report ==="
python -m coverage report -m

# Generate HTML coverage report
python -m coverage html
echo -e "\nHTML coverage report generated in htmlcov/index.html"