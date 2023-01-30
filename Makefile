#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := `pwd`

#* Installation
.PHONY: install
install:
	pip install .

#* Build wheel
.PHONY: wheel
wheel:
	pip wheel .

#* Uninstall
#* Installation
.PHONY: uninstall
uninstall:
	pip uninstall iris_velociraptorartifact_module

#* Cleanup
.PHONY: wheel-remove
wheel-remove:
	find . | grep -E "iris_velociraptorartifact_module" | grep -E ".whl" | xargs rm -rf

.PHONY: egg-remove
egg-remove:
	find . | grep -E ".egg-info" | xargs rm -rf

.PHONY: build-remove
build-remove:
	rm -rf build/

.PHONY: clean
clean: build-remove egg-remove wheel-remove