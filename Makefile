# Makefile for XC8 Wrapper development and testing

# Python interpreter
PYTHON := python

# Package name
PACKAGE := xc8_wrapper

# Test directories
TEST_DIR := tests
SRC_DIR := $(PACKAGE)

# Coverage settings
COVERAGE_MIN := 78
COVERAGE_HTML_DIR := htmlcov

# Virtual environment
VENV_DIR := .venv
VENV_ACTIVATE := $(VENV_DIR)/Scripts/activate

.PHONY: help install install-dev test test-fast test-slow test-coverage test-unit test-integration test-performance test-compatibility lint format type-check security clean build upload docs pre-commit setup-dev

help:
	@echo "XC8 Wrapper Development Commands"
	@echo "================================"
	@echo ""
	@echo "Setup:"
	@echo "  setup-dev         Set up development environment"
	@echo "  install           Install package"
	@echo "  install-dev       Install package with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test              Run all tests"
	@echo "  test-fast         Run only fast tests"
	@echo "  test-slow         Run only slow tests"
	@echo "  test-coverage     Run tests with coverage report"
	@echo "  test-unit         Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-performance  Run performance tests only"
	@echo "  test-compatibility Run compatibility tests only"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint              Run linting (flake8)"
	@echo "  format            Format code (black + isort)"
	@echo "  type-check        Run type checking (mypy)"
	@echo "  security          Run security checks"
	@echo "  pre-commit        Run pre-commit hooks"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  clean             Clean build artifacts"
	@echo "  build             Build package"
	@echo "  upload            Upload to PyPI"
	@echo "  docs              Build documentation"

# Setup development environment
setup-dev:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_ACTIVATE) && pip install --upgrade pip
	$(VENV_ACTIVATE) && pip install -e .[dev]
	$(VENV_ACTIVATE) && pre-commit install

# Install package
install:
	$(PYTHON) -m pip install -e .

# Install with development dependencies
install-dev:
	$(PYTHON) -m pip install -e .[dev]

# Run all tests
test:
	$(PYTHON) -m pytest $(TEST_DIR) -v

# Run only fast tests
test-fast:
	$(PYTHON) -m pytest $(TEST_DIR) -v -m "not slow"

# Run only slow tests
test-slow:
	$(PYTHON) -m pytest $(TEST_DIR) -v -m "slow"

# Run tests with coverage
test-coverage:
	$(PYTHON) -m pytest $(TEST_DIR) \
		--cov=$(PACKAGE) \
		--cov-report=term-missing \
		--cov-report=html:$(COVERAGE_HTML_DIR) \
		--cov-report=xml \
		--cov-fail-under=$(COVERAGE_MIN) \
		-v

# Run unit tests only
test-unit:
	$(PYTHON) -m pytest $(TEST_DIR) -v -m "unit"

# Run integration tests only
test-integration:
	$(PYTHON) -m pytest $(TEST_DIR) -v -m "integration"

# Run performance tests only
test-performance:
	$(PYTHON) -m pytest $(TEST_DIR)/test_performance.py -v

# Run compatibility tests only
test-compatibility:
	$(PYTHON) -m pytest $(TEST_DIR)/test_compatibility.py -v

# Run linting
lint:
	$(PYTHON) -m flake8 $(SRC_DIR) $(TEST_DIR) --count --statistics

# Format code
format:
	$(PYTHON) -m black $(SRC_DIR) $(TEST_DIR)
	$(PYTHON) -m isort $(SRC_DIR) $(TEST_DIR)

# Run type checking
type-check:
	$(PYTHON) -m mypy $(SRC_DIR) --ignore-missing-imports

# Run security checks
security:
	$(PYTHON) -m safety check
	$(PYTHON) -m bandit -r $(SRC_DIR)

# Run pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(COVERAGE_HTML_DIR)/
	rm -f coverage.xml
	rm -f .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Build package
build: clean
	$(PYTHON) -m build

# Upload to PyPI (requires proper credentials)
upload: build
	$(PYTHON) -m twine check dist/*
	$(PYTHON) -m twine upload dist/*

# Build documentation
docs:
	@echo "Documentation building not yet implemented"

# Run a comprehensive test suite
test-all: test-coverage lint type-check security
	@echo "All tests and checks completed successfully!"

# Quick development test
quick-test:
	$(PYTHON) run_tests.py

# Continuous integration simulation
ci-test:
	$(PYTHON) -m pytest $(TEST_DIR) --cov=$(PACKAGE) --cov-report=xml -v
	$(PYTHON) -m flake8 $(SRC_DIR) $(TEST_DIR) --count --statistics
	$(PYTHON) -m black --check $(SRC_DIR) $(TEST_DIR)
	$(PYTHON) -m isort --check-only $(SRC_DIR) $(TEST_DIR)
	$(PYTHON) -m mypy $(SRC_DIR) --ignore-missing-imports
	$(PYTHON) -m safety check
	$(PYTHON) -m bandit -r $(SRC_DIR)

# Development workflow
dev: format lint type-check test-fast
	@echo "Development checks completed!"

# Release preparation
release-prep: clean test-all build
	@echo "Release preparation completed!"
	@echo "Ready to upload to PyPI with: make upload"
