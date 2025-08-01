# ADCC Analysis Engine v0.6 - Test Organization

## Test Structure

```
tests/
├── unit/           # Unit tests for individual modules
├── integration/    # Integration tests for module interactions
├── e2e/           # End-to-end tests for complete workflows
├── fixtures/      # Test fixtures, templates, and utilities
├── data/          # Test data files
└── README.md      # This file
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Individual module functionality
- Isolated component testing
- Mock external dependencies
- Fast execution (< 1 second per test)

### Integration Tests (`tests/integration/`)
- Module interaction testing
- Data flow between components
- Real file system operations
- Medium execution time (1-10 seconds per test)

### End-to-End Tests (`tests/e2e/`)
- Complete workflow testing
- Full data pipeline testing
- Web UI functionality
- Slow execution (10+ seconds per test)

### Test Fixtures (`tests/fixtures/`)
- Test templates and base classes
- Common test utilities
- Mock data generators
- Test configuration files

### Test Data (`tests/data/`)
- Sample CSV files
- Sample Excel files
- Sample JSON files
- Test configuration files

## Test Naming Convention

- Unit tests: `test_[module_name].py`
- Integration tests: `test_[module1]_[module2]_integration.py`
- E2E tests: `test_[workflow_name]_e2e.py`
- Fixtures: `[name]_template.py` or `[name]_fixture.py`

## Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_athlete_profiles.py

# Run with verbose output
pytest -v
```

## Test Data Management

- Test data should be minimal but realistic
- Use fixtures for common test data
- Clean up test data after each test
- Don't use production data in tests
- Version control test data files

## Test Quality Standards

- All tests must have descriptive names
- All tests must have docstrings
- Tests should be independent and repeatable
- Tests should clean up after themselves
- Tests should provide clear error messages
- Aim for 80%+ code coverage 