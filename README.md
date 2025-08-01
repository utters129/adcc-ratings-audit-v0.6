# ADCC Analysis Engine v0.6

A comprehensive data analytics platform for ADCC (Abu Dhabi Combat Club) tournament operations, athlete evaluation, and competitive integrity.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp env.example .env
# Edit .env with your settings

# Install pre-commit hooks
pre-commit install

# Run the development setup
python context/setup_dev.py
```

## Project Structure

```
├── src/                    # Source code
│   ├── config/            # Configuration modules
│   ├── data_acquisition/  # File download and acquisition
│   ├── data_processing/   # Data cleaning and processing
│   ├── analytics/         # Glicko ratings and analytics
│   ├── web_ui/           # FastAPI web interface
│   └── utils/            # Utility functions
├── data/                  # Data storage
│   ├── raw/              # Raw downloaded files
│   ├── processed/        # Processed data files
│   └── datastore/        # JSON dictionaries and metadata
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── e2e/             # End-to-end tests
│   └── fixtures/        # Test fixtures and utilities
├── context/              # Documentation and setup files
├── logs/                 # Application logs
└── docs/                 # Generated documentation
```

## Documentation

- **Architecture**: `context/Architecture_v0.6.md`
- **Development Roadmap**: `context/Development_Roadmap_v0.6.md`
- **Development Checklist**: `context/Development_CHECKLIST.md`
- **Executive Summary**: `context/Executive_Summary_v0.6.md`
- **Test Organization**: `tests/README.md`

## Development

```bash
# Run tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=src --cov-report=html

# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/
```

## Deployment

```bash
# Deploy to Railway
railway up
```

## Features

- **Data Acquisition**: Semi-automated Smoothcomp file downloads
- **Data Processing**: Robust cleaning and normalization
- **Analytics**: Glicko-2 rating system with skill-level dependent starting ratings
- **Web Interface**: Multi-level access (Public, Admin, Developer)
- **Tournament Tools**: Seeding recommendations, registration auditing
- **Performance Tracking**: Historical ratings and match analysis

## License

Private - ADCC Internal Use Only

## Version

v0.6.0-alpha.6 