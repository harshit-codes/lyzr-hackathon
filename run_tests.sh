#!/bin/bash
# Test runner script for SuperSuite Streamlit Application

echo "========================================="
echo "SuperSuite Streamlit Application Tests"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install pytest pytest-cov pytest-mock"
    exit 1
fi

echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -q pytest pytest-cov pytest-mock pandas streamlit 2>/dev/null || true

echo ""
echo -e "${YELLOW}Running tests...${NC}"
echo ""

# Run tests with coverage
pytest tests/ \
    -v \
    --tb=short \
    --cov=app \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml \
    --color=yes

TEST_EXIT_CODE=$?

echo ""
echo "========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
fi
echo "========================================="
echo ""

# Show coverage summary
if [ -f ".coverage" ]; then
    echo -e "${YELLOW}Coverage report generated:${NC}"
    echo "  - HTML: htmlcov/index.html"
    echo "  - XML: coverage.xml"
    echo ""
fi

exit $TEST_EXIT_CODE

