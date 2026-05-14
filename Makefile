# Makefile for ai-helpers

# Container runtime (podman or docker)
CONTAINER_RUNTIME ?= $(shell command -v podman 2>/dev/null || echo docker)

# skillsaw image
SKILLSAW_IMAGE = ghcr.io/stbenjam/skillsaw:0.8.0

# Detect if SELinux is enforcing and add security option
SELINUX_OPT := $(shell if command -v getenforce >/dev/null 2>&1 && [ "$$(getenforce 2>/dev/null)" = "Enforcing" ]; then echo "--security-opt label=disable"; fi)

.PHONY: help
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: lint
lint: ## Run plugin linter (verbose, strict mode)
	$(CONTAINER_RUNTIME) run --rm --platform linux/amd64 $(SELINUX_OPT) -v $(PWD):/workspace:Z $(SKILLSAW_IMAGE) -v --strict .

.PHONY: lint-pull
lint-pull: ## Pull the latest skillsaw image
	$(CONTAINER_RUNTIME) pull $(SKILLSAW_IMAGE)

.PHONY: update
update: ## Update plugin documentation and website data
	@echo "Fixing frontmatter quotes, if any..."
	@python3 scripts/fix_frontmatter_quotes.py
	@echo "Syncing marketplace versions..."
	@python3 scripts/sync_marketplace_versions.py
	@echo "Updating plugin documentation..."
	@python3 scripts/generate_plugin_docs.py
	@echo "Building website data..."
	@python3 scripts/build-website.py

.PHONY: eval
eval: ## Run all agentic documentation evaluation tests (~30-60 min)
	@echo "Running all evaluation tests..."
	@cd plugins/agentic-docs && npx promptfoo@latest eval -c promptfooconfig.yaml

.PHONY: eval-navigation
eval-navigation: ## Run navigation tests only
	@echo "Running navigation tests..."
	@cd plugins/agentic-docs && npx promptfoo@latest eval -c promptfooconfig.yaml --filter-description "Navigation:"

.PHONY: eval-authoring
eval-authoring: ## Run enhancement authoring tests only
	@echo "Running authoring tests..."
	@cd plugins/agentic-docs && npx promptfoo@latest eval -c promptfooconfig.yaml --filter-description "Authoring:"

.PHONY: eval-anti-pattern
eval-anti-pattern: ## Run anti-pattern tests only
	@echo "Running anti-pattern tests..."
	@cd plugins/agentic-docs && npx promptfoo@latest eval -c promptfooconfig.yaml --filter-description "Anti-pattern:"

.PHONY: eval-view
eval-view: ## Open evaluation results in web UI
	@cd plugins/agentic-docs && npx promptfoo@latest view

.PHONY: eval-clean
eval-clean: ## Clear evaluation cache and results
	@echo "Cleaning evaluation cache..."
	@rm -rf plugins/agentic-docs/.work/eval/
	@cd plugins/agentic-docs && npx promptfoo@latest cache clear

.DEFAULT_GOAL := help
