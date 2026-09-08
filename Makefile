# 3d-models -- build & regression entry points.
# `make` with no target prints this list.

PY ?= python

.DEFAULT_GOAL := help
.PHONY: help test check build-all build clean setup regen list

help:  ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[1m%-12s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "  build one model:   make build MODEL=opengrid-needle-holder"

test:  ## rebuild every model (except .modelignore) and assert it still builds
	$(PY) -m pytest

check:  ## strict gate for CI: fast rebuild of all models, warnings are failures
	$(PY) build.py --all --strict --no-png

build-all:  ## rebuild every model with previews, print a pass/fail summary
	$(PY) build.py --all

build:  ## build a single model: make build MODEL=<name>
	@test -n "$(MODEL)" || { echo "usage: make build MODEL=<name>"; exit 2; }
	$(PY) build.py models/$(MODEL)

list:  ## list the models the regression covers
	@$(PY) -c "from build import iter_models; [print(s.parent.name) for s in iter_models()]"

clean:  ## delete build artifacts
	rm -rf build/

setup:  ## install python deps (+ OpenSCAD toolchain for MOUNTS)
	$(PY) -m pip install -r requirements.txt
	bash lib/connectors/vendor/regenerate.sh

regen:  ## re-render the vendored connector STLs (needs network)
	bash lib/connectors/vendor/regenerate.sh
