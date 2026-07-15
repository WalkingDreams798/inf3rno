# Contributing to Inf3rno

Thank you for your interest in contributing to Inf3rno! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

Please be respectful and professional in all interactions. We are committed to providing a welcoming and constructive environment for everyone.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/inf3rno.git
   cd inf3rno
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/WalkingDreams798/inf3rno.git
   ```
4. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest flake8 black isort bandit
   ```
3. Install pre-commit hooks (optional):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Making Changes

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `ci/` - CI/CD changes

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(ssh): add key-based authentication support`
- `fix(http): handle timeout exceptions`
- `docs(readme): update installation guide`
- `test(modules): add unit tests for SSH module`

## Testing

Run tests before submitting:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=inf3rno

# Run specific test file
pytest tests/test_inf3rno.py -v
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit pull request with clear description

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No new warnings
- [ ] All tests pass

## Style Guidelines

### Python Style

- Follow PEP 8
- Use Black for formatting:
  ```bash
  black inf3rno/
  ```
- Use isort for imports:
  ```bash
  isort inf3rno/
  ```

### Linting

Run linters before committing:

```bash
# Flake8
flake8 inf3rno/

# Bandit (security)
bandit -r inf3rno/
```

### Type Hints

Use type hints where appropriate:

```python
def process_data(data: List[str], count: int) -> Dict[str, Any]:
    pass
```

## Adding New Modules

1. Create new file in `modules/` directory
2. Inherit from `BaseBrute`
3. Implement `try_login` method
4. Add to `inf3rno/__init__.py`
5. Update CLI in `inf3rno/cli.py`
6. Add tests

## Adding Plugins

See [Plugin System Documentation](docs/plugin-system.md)

## Questions?

Feel free to open an issue for any questions about contributing!
