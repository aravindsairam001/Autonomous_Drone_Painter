# Makefile for PX4 Autonomous Wall Spray Painting System

.PHONY: help install install-dev test clean format lint type-check docs run-wall-generator run-spawn-updater run-painter

# Default target
help:
	@echo "PX4 Autonomous Wall Spray Painting System"
	@echo "========================================="
	@echo ""
	@echo "Available targets:"
	@echo "  install         - Install the package and dependencies"
	@echo "  install-dev     - Install with development dependencies"
	@echo "  install-venv    - Install in a virtual environment"
	@echo "  test           - Run tests"
	@echo "  clean          - Clean up build artifacts and cache"
	@echo "  format         - Format code with black"
	@echo "  lint           - Run linting with flake8"
	@echo "  type-check     - Run type checking with mypy"
	@echo "  docs           - Generate documentation"
	@echo "  run-wall-generator    - Run the wall generator script"
	@echo "  run-spawn-updater     - Run the drone spawn updater script"
	@echo "  run-painter          - Run the spray painting script"
	@echo "  px4-setup       - Instructions for PX4 setup"

# Installation targets
install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

install-venv:
	./install.sh --venv

# Development targets
test:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

format:
	black *.py
	isort *.py

lint:
	flake8 *.py --max-line-length=88 --ignore=E203,W503

type-check:
	mypy *.py --ignore-missing-imports

docs:
	@echo "Generating documentation..."
	@echo "Documentation is mainly in README.md"
	@echo "For Sphinx docs, run: sphinx-build -b html docs/ docs/_build/"

# Application targets
run-wall-generator:
	python3 interactive_wall_generator.py

run-spawn-updater:
	python3 update_drone_spawn_pose.py

run-painter:
	python3 wall_spray_painting_advanced.py

# PX4 setup instructions
px4-setup:
	@echo "PX4 Autopilot Setup Instructions"
	@echo "================================"
	@echo ""
	@echo "1. Clone PX4 Autopilot:"
	@echo "   git clone https://github.com/PX4/PX4-Autopilot.git"
	@echo "   cd PX4-Autopilot"
	@echo ""
	@echo "2. Build for SITL simulation:"
	@echo "   make px4_sitl_default gazebo-classic"
	@echo ""
	@echo "3. Copy scripts to PX4 Tools directory:"
	@echo "   cp *.py /path/to/PX4-Autopilot/Tools/"
	@echo ""
	@echo "4. Run the complete workflow:"
	@echo "   make run-wall-generator"
	@echo "   make run-spawn-updater"
	@echo "   # Start PX4 SITL in one terminal:"
	@echo "   ./launch_with_spawn.sh"
	@echo "   # Run painter in another terminal:"
	@echo "   make run-painter"

# Development workflow
dev-setup: install-dev
	pre-commit install

dev-check: format lint type-check test

# Quick workflow targets
quick-setup: install run-wall-generator run-spawn-updater
	@echo "Quick setup complete!"
	@echo "Now start PX4 SITL and run the painter."

full-workflow: install run-wall-generator run-spawn-updater
	@echo "🚀 Full workflow setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Terminal 1: ./launch_with_spawn.sh"
	@echo "2. Terminal 2: make run-painter"
