# Contributing to XC8 Wrapper

Thank you for your interest in contributing to the XC8 Wrapper project! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/s-celles/xc8-wrapper.git
   cd xc8-wrapper
   ```
3. **Set up the development environment**:
   ```bash
   python setup_dev.py
   ```
4. **Activate the virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - Unix/macOS: `source .venv/bin/activate`
5. **Run tests** to ensure everything works:
   ```bash
   python -m pytest tests/ -v
   ```

## 🛠️ Development Workflow

### Setting Up Your Development Environment

We provide several ways to set up your development environment:

1. **Automated setup** (recommended):
   ```bash
   python setup_dev.py
   ```

2. **Manual setup**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Unix/macOS
   # or
   .venv\Scripts\activate     # Windows

   pip install -e .[dev]
   pre-commit install
   ```

3. **Using Makefile** (Unix/macOS):
   ```bash
   make setup-dev
   ```

### Running Tests

We have comprehensive test coverage. Here are the main test commands:

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=xc8_wrapper --cov-report=html

# Run quick tests (exclude slow tests)
python -m pytest tests/ -v -m "not slow"

# Run specific test categories
python -m pytest tests/test_core.py -v           # Core functionality
python -m pytest tests/test_cli.py -v            # CLI interface
python -m pytest tests/test_integration.py -v    # Integration tests
python -m pytest tests/test_performance.py -v    # Performance tests
python -m pytest tests/test_compatibility.py -v  # Compatibility tests

# Quick test runner
python run_tests.py
```

### Code Quality

We maintain high code quality standards:

```bash
# Format code
black xc8_wrapper tests
isort xc8_wrapper tests

# Lint code
flake8 xc8_wrapper tests

# Type checking
mypy xc8_wrapper --ignore-missing-imports

# Security checks
safety check
bandit -r xc8_wrapper

# Run all quality checks
make dev  # or make ci-test
```

### Pre-commit Hooks

We use pre-commit hooks to maintain code quality:

```bash
# Install hooks (done automatically by setup_dev.py)
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

## 📋 Contribution Guidelines

### Code Style

- **Python**: Follow PEP 8, enforced by `black` and `flake8`
- **Line length**: 127 characters (configured in setup.cfg)
- **Imports**: Sorted with `isort`, using the `black` profile
- **Type hints**: Use type hints where appropriate
- **Docstrings**: Use Google-style docstrings

### Testing

- **Coverage**: Maintain at least 80% test coverage
- **Test types**: Include unit, integration, and performance tests
- **Test naming**: Use descriptive test names that explain what is being tested
- **Mocking**: Use `unittest.mock` for external dependencies

### Documentation

- **README**: Update if you add new features
- **Docstrings**: Document all public functions and classes
- **Comments**: Add comments for complex logic
- **Examples**: Include usage examples for new features

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat(cli): add support for custom optimization levels
fix(core): handle unicode paths correctly
docs(readme): update installation instructions
test(core): add tests for edge cases
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Python version** and operating system
2. **XC8 Wrapper version**
3. **Steps to reproduce** the issue
4. **Expected behavior** vs actual behavior
5. **Error messages** or stack traces
6. **Minimal code example** if applicable

Use the bug report template in GitHub Issues.

## 💡 Feature Requests

For feature requests, please:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and motivation
3. **Provide examples** of how the feature would be used
4. **Consider implementation** if possible

Use the feature request template in GitHub Issues.

## 🔧 Development Guide

### Project Structure

```
xc8-wrapper/
├── xc8_wrapper/           # Main package
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # Command-line interface
│   └── core.py           # Core functionality
├── tests/                # Test suite
│   ├── test_core.py      # Core tests
│   ├── test_cli.py       # CLI tests
│   ├── test_integration.py  # Integration tests
│   ├── test_performance.py  # Performance tests
│   ├── test_compatibility.py # Compatibility tests
│   └── test_utils.py     # Utility tests
├── .github/workflows/    # GitHub Actions
├── demo.py              # Demo script
├── setup_dev.py         # Development setup
├── run_tests.py         # Test runner
├── pyproject.toml       # Package configuration
└── README.md           # Documentation
```

### Adding New Features

1. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement the feature** following our code style

3. **Add tests** for your feature:
   - Unit tests in appropriate test files
   - Integration tests if needed
   - Update existing tests if they're affected

4. **Update documentation**:
   - Add docstrings to new functions/classes
   - Update README if needed
   - Add examples to demo.py if appropriate

5. **Run all tests** and quality checks:
   ```bash
   make dev
   ```

6. **Commit your changes** with a good commit message

7. **Push to your fork** and create a pull request

### Testing Guidelines

- **Write tests first** (TDD approach preferred)
- **Test edge cases** and error conditions
- **Use descriptive test names**
- **Mock external dependencies** (file system, network, etc.)
- **Test across platforms** when possible

### Performance Considerations

- **Profile before optimizing**
- **Add performance tests** for critical paths
- **Consider memory usage** for large operations
- **Test with realistic data sizes**

## 📦 Release Process

Releases are handled by maintainers:

1. **Version bump** in `pyproject.toml`
2. **Update changelog** (if maintained)
3. **Create release PR**
4. **Tag release** after merge
5. **GitHub Actions** handles building and publishing

## 🤝 Community

- **Be respectful** and constructive
- **Help others** with questions and issues
- **Follow the code of conduct**
- **Contribute to discussions**

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: Contact the maintainers directly if needed

## 🏆 Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes (for significant contributions)
- README acknowledgments (for major features)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to XC8 Wrapper! Your help makes this project better for everyone. 🎉
