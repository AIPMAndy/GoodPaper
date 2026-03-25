# Contributing to GoodPaper

Thank you for your interest in contributing to GoodPaper! This document provides guidelines for contributing.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/AIPMAndy/GoodPaper.git
cd GoodPaper

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
pytest tests/
```

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in [Issues](https://github.com/AIPMAndy/GoodPaper/issues)
- If not, create a new issue using the bug report template
- Include detailed steps to reproduce
- Provide sample files if possible

### Suggesting Features

- Open an issue using the feature request template
- Describe the use case clearly
- Explain why this feature would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure tests pass (`pytest tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Code Style

- Follow PEP 8 for Python code
- Add docstrings for public functions
- Keep functions focused and small
- Add type hints where appropriate

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for good test coverage

## Questions?

Feel free to open an issue for any questions!
