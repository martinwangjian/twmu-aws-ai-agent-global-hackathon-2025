#!/bin/bash
# Test A2A agent locally or against deployed endpoint

set -e

# Configuration
A2A_TEST_URL="${A2A_TEST_URL:-http://localhost:9000}"
SKIP_INTEGRATION="${SKIP_INTEGRATION_TESTS:-false}"

echo "🧪 Testing A2A Agent"
echo "Target: $A2A_TEST_URL"
echo ""

# Run functional tests
echo "Running functional tests..."
A2A_TEST_URL="$A2A_TEST_URL" \
SKIP_INTEGRATION_TESTS="$SKIP_INTEGRATION" \
uv run pytest tests/test_a2a_functional.py -v

# Run BDD tests
echo ""
echo "Running BDD tests..."
A2A_TEST_URL="$A2A_TEST_URL" \
SKIP_INTEGRATION_TESTS="$SKIP_INTEGRATION" \
uv run pytest tests/test_a2a_agent_bdd.py -v --gherkin-terminal-reporter

# Run endpoint regression tests (integration only)
if [ "$SKIP_INTEGRATION" != "true" ]; then
    echo ""
    echo "Running endpoint regression tests..."
    uv run pytest tests/test_a2a_endpoints.py -v -m integration
fi

echo ""
echo "✅ All tests passed!"
