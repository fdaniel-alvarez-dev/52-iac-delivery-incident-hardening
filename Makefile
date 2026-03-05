.PHONY: setup demo test lint clean

PYTHON ?= python3
VENV ?= .venv
VENV_PY := $(VENV)/bin/python
PYTHONPATH := src

setup:
	$(PYTHON) -m venv $(VENV)
	mkdir -p artifacts

demo: setup
	PYTHONPATH=$(PYTHONPATH) $(VENV_PY) -m portfolio_proof report --examples examples --out artifacts/report.md
	@echo "Generated artifacts/report.md"

lint: setup
	PYTHONPATH=$(PYTHONPATH) $(VENV_PY) -m compileall -q src tests scripts
	PYTHONPATH=$(PYTHONPATH) $(VENV_PY) -m portfolio_proof validate --examples examples

test: setup
	PYTHONPATH=$(PYTHONPATH) $(VENV_PY) -m unittest discover -s tests -p 'test_*.py' -q

clean:
	rm -rf artifacts .venv
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
