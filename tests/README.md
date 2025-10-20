# Test Suite

Comprehensive test coverage for the AWS AI Agent booking system.

## Test Organization

```
tests/
├── unit/                          # Fast, isolated tests
│   ├── test_ssm_config.py        # SSM configuration
│   └── test_response_cleaning.py # Response formatting
│
├── functional/                    # Component integration (future)
│   └── (planned)
│
├── e2e/                          # End-to-end flows
│   ├── test_booking_flow.py          # Complete booking flow
│   ├── test_calendar_tools.py        # Calendar Gateway integration
│   ├── test_a2a_booking_no_hallucination.py  # Hallucination prevention
│   └── test_e2e_memory.py            # Memory integration
│
└── integration/                  # External service integration
    ├── test_a2a_endpoints.py         # A2A agent endpoints
    └── test_a2a_agent_bdd.py         # BDD scenarios
```

## Running Tests

### All Tests

```bash
uv run pytest
```

### By Category

```bash
# Unit tests only (fast)
uv run pytest -m unit

# E2E tests only (requires deployment)
uv run pytest -m e2e

# Integration tests only
uv run pytest -m integration

# Exclude slow tests
uv run pytest -m "not slow"
```

### Specific Test Files

```bash
# Run single test file
uv run pytest tests/e2e/test_booking_flow.py -v

# Run specific test
uv run pytest tests/e2e/test_booking_flow.py::test_complete_booking_flow -v
```

### With Coverage

```bash
uv run pytest --cov=src tests/
```

## Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.unit` - Fast unit tests, no external dependencies
- `@pytest.mark.functional` - Component integration tests
- `@pytest.mark.integration` - Tests requiring deployed services
- `@pytest.mark.e2e` - End-to-end tests requiring full deployment
- `@pytest.mark.slow` - Tests taking > 10 seconds

## Critical Tests

### Hallucination Prevention

**`test_a2a_booking_no_hallucination.py`** - Prevents regression of the booking hallucination bug where the agent would fabricate event IDs without calling the calendar API.

**What it tests**:

- Agent calls `checkAvailability` before booking
- Agent calls `createEvent` to create actual calendar event
- Real event ID is returned (not fabricated)
- Event exists in Google Calendar with correct details

**Why critical**: This bug caused bookings to appear confirmed but never actually be created in the calendar.

### Booking Flow

**`test_booking_flow.py`** - Validates the complete booking workflow from user request to calendar event creation.

### Calendar Tools

**`test_calendar_tools.py`** - Tests Gateway → Lambda → Google Calendar integration for all calendar operations.

## Test Data

### Calendar Test Data

- Uses dedicated test calendar ID from environment
- Cleans up test events after each test
- Uses future dates to avoid conflicts

### Environment Variables

Required for E2E tests:

```bash
GOOGLE_CALENDAR_ID=<test-calendar-id>
A2A_AGENT_URL=<deployed-a2a-agent-url>
```

## CI/CD Integration

### Local Development

```bash
# Pre-commit: Run fast tests
uv run pytest -m unit

# Pre-push: Run all tests except E2E
uv run pytest -m "not e2e"
```

### CI Pipeline

```yaml
stages:
  - unit: pytest -m unit # Always run
  - functional: pytest -m functional # Always run
  - integration: pytest -m integration # On PR to main
  - e2e: pytest -m e2e # On merge to main
```

## Test Quality Standards

- **Independence**: Tests must not depend on execution order
- **Cleanup**: Tests must clean up resources (calendar events, etc.)
- **Clear failures**: Assertion messages must explain what went wrong
- **Fast execution**: Unit tests < 1s, functional < 10s, E2E < 30s
- **No flakiness**: Tests must pass consistently (> 99% pass rate)

## Adding New Tests

1. Choose appropriate directory (`unit/`, `functional/`, `e2e/`, `integration/`)
2. Add pytest marker (`@pytest.mark.unit`, etc.)
3. Follow naming convention: `test_<feature>.py`
4. Add docstrings explaining what and why
5. Clean up resources in fixtures or teardown
6. Update this README if adding new test category

## Troubleshooting

### Google Calendar Token Not Found

```bash
# Generate token using OAuth flow
python scripts/setup_google_calendar.py
```

### A2A Agent URL Not Set

```bash
# Get deployed agent URL
uv run agentcore status

# Set environment variable
export A2A_AGENT_URL=<agent-url>
```

### Lambda Function Not Found

```bash
# Deploy CDK stacks
cd cdk_infra
uv run cdk deploy --all
```

## Test Coverage Goals

- **Unit tests**: > 80% code coverage
- **Integration tests**: All critical paths covered
- **E2E tests**: All user flows covered
- **Regression tests**: All fixed bugs have tests
