RYE_EXEC ?= rye run
PYTHON_VERSION ?= 3.12
PATH := $(HOME)/.rye/shims:$(PATH)

SHELL := /bin/bash
PYTHON_FILES := $(shell find src/$(PROJECT_NAME) -type f -name '*.py' -o -name '*.pyi')

USE_UV ?= true
REQUIRED_UV_VERSION ?= 0.2.2
REQUIRED_RYE_VERSION ?= 0.34.0
bootstrap:
	@INSTALLED_UV_VERSION=$$(uv --version 2>/dev/null | awk '{print $$2}' || echo "0.0.0"); \
    UV_VERSION=$$(printf '%s\n' "$(REQUIRED_UV_VERSION)" "$$INSTALLED_UV_VERSION" | sort -V | head -n1); \
	if [ "$$UV_VERSION" != "$(REQUIRED_UV_VERSION)" ]; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@INSTALLED_RYE_VERSION=$$(rye --version 2>/dev/null | head -n1 | awk '{print $$2}' || echo "0.0.0"); \
	DETECTED_RYE_VERSION=$$(printf '%s\n' "$(REQUIRED_RYE_VERSION)" "$$INSTALLED_RYE_VERSION" | sort -V | head -n1); \
	if [ "$$DETECTED_RYE_VERSION" != "$(REQUIRED_RYE_VERSION)" ]; then \
		rye self update || curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" RYE_VERSION="$(REQUIRED_RY_VERSION)" bash; \
	fi
	@rye config --set-bool behavior.use-uv=$(USE_UV)
	@rye pin --relaxed $(PYTHON_VERSION)

install: bootstrap
	@rye sync --no-lock
	@cp requirements-dev.lock requirements-dev-py$$(echo $(PYTHON_VERSION) | sed "s/\.//").lock
.PHONY: install

sync: bootstrap
	@rye sync --no-lock
.PHONY: sync

lock: bootstrap
	@rye sync
	@cp requirements-dev.lock requirements-dev-py$$(echo $(PYTHON_VERSION) | sed "s/\.//").lock
.PHONY: lock

build: sync
	@rye build
.PHONY: build


format:
	@$(RYE_EXEC) ruff check --fix src/ tests/
	@$(RYE_EXEC) ruff format src/ tests/
	@$(RYE_EXEC) isort src/ tests/
.PHONY: format

lint:
	@$(RYE_EXEC) ruff check src/ tests/
	@$(RYE_EXEC) ruff format --check src/ tests/
	@$(RYE_EXEC) isort --check src/ tests/
.PHONY: lint

test:
	@$(RYE_EXEC) tox -e system-unit,system-greenlets -- -n auto
.PHONY: test

doctest:
	@$(RYE_EXEC) tox -e system-doctest
.PHONY: test

mypy:
	@$(RYE_EXEC) tox -e system-staticcheck
.PHONY: mypy

docs/build:
	make SPHINXBUILD="$(RYE_EXEC) sphinx-build" -C docs html
.PHONY: docs/build


CADDY_IMAGE ?= caddy:2.7-alpine
CADDY_SERVER_PORT ?= 9999
docs/browse: docs/build
	@docker run --rm --network host \
        -v $(PWD)/docs/build/html/:/var/www \
        -it $(CADDY_IMAGE) \
	    caddy file-server --browse --listen :$(CADDY_SERVER_PORT) --root /var/www
.PHONY: docs/browse
