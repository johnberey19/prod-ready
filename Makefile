.PHONY: install lint test test-unit test-integration validate build clean

install:
	pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/
	mypy src/prod_ready/

format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

test: test-unit test-integration

test-unit:
	pytest tests/unit/ -v --cov=prod_ready --cov-report=term-missing

test-integration:
	pytest tests/integration/ -v

validate:
	pytest tests/integration/test_validation.py -v --tb=short

build:
	python -m build
	twine check dist/*

clean:
	rm -rf dist/ build/ *.egg-info .mypy_cache .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
