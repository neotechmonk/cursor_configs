# TradeX Strategy Testing Guide

Documents specifics related to structure, fixtures and mocks on the test suite

## TODO
## Test Structure

tests/
├── conftest.py              # Shared pytest fixtures; other fixtures are in the test files
├── test_xxxx.py             # Root level test
├── module/
│   └── test_yyy.py          # Module level test
└── mocks/                   # Mock data and functions
└── data                     # Mimics third-party data


## Running Tests
To run the entire test suite:
```bash
pytest
```

To run specific test categories:
```bash
pytest  -v -ss --tb=short tests/test_strategy_runner.py # specific files
pytest -k "config"                                      # Run all tests with "config" in their name
```


## Important Notes

1. The test suite uses temporary directories for strategy configurations
2. Mock functions are designed to simulate real strategy behavior

## Dependencies

- pytest
- pandas
- pyyaml

