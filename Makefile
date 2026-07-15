# Inf3rno Makefile
# Multi-Protocol Brute-Force Tool

.PHONY: install uninstall clean test help

PYTHON = python3
PIP = $(PYTHON) -m pip
PACKAGE = inf3rno

help: ## Show this help
	@echo ""
	@echo "Inf3rno - Multi-Protocol Brute-Force Tool"
	@echo "========================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install Inf3rno and dependencies
	@echo "[*] Installing Inf3rno..."
	$(PIP) install --break-system-packages -r requirements.txt
	$(PIP) install --break-system-packages -e .
	@chmod +x inf3rno/cli.py
	@echo "[+] Installation complete!"
	@echo "[*] Run: python3 inf3rno/cli.py --help"

install-system: ## Install system-wide (requires root)
	@echo "[*] Installing Inf3rno system-wide..."
	$(PIP) install -r requirements.txt
	$(PIP) install .
	@echo "[+] System-wide installation complete!"

uninstall: ## Uninstall Inf3rno
	@echo "[*] Uninstalling Inf3rno..."
	$(PIP) uninstall -y $(PACKAGE)
	@echo "[+] Uninstall complete!"

clean: ## Clean build artifacts
	@echo "[*] Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info .eggs/
	rm -rf __pycache__ **/__pycache__ *.pyc
	rm -rf .pytest_cache/ .tox/ htmlcov/
	rm -rf output/*.txt output/*.json output/*.html output/*.csv
	rm -rf output/.state.json
	@echo "[+] Clean complete!"

test: ## Run tests
	@echo "[*] Running tests..."
	$(PYTHON) -m pytest tests/ -v

lint: ## Run linter
	@echo "[*] Running linter..."
	$(PYTHON) -m flake8 inf3rno/ --max-line-length=100

format: ## Format code with black
	@echo "[*] Formatting code..."
	$(PYTHON) -m black inf3rno/

run: ## Run Inf3rno (usage: make run ARGS="-t 192.168.1.1 --ssh")
	$(PYTHON) inf3rno/cli.py $(ARGS)

generate: ## Generate passwords (usage: make generate ARGS="--smart -t example.com")
	$(PYTHON) inf3rno/cli.py $(ARGS)

version: ## Show version
	@$(PYTHON) -c "from inf3rno import __version__; print(__version__)"

deps: ## Show dependencies
	@echo "Dependencies:"
	@cat requirements.txt

install-deps: ## Install development dependencies
	$(PIP) install --break-system-packages pytest flake8 black

help-commands: ## Show usage examples
	@echo ""
	@echo "Usage Examples:"
	@echo "  make install                          # Install Inf3rno"
	@echo "  make run ARGS='-t 192.168.1.1 --ssh'  # Run SSH brute-force"
	@echo "  make generate ARGS='--smart -t host'  # Generate wordlist"
	@echo "  make clean                            # Clean artifacts"
	@echo ""
