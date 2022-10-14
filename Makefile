.DEFAULT_GOAL := help

install-dependencies:
	pip install poetry==1.2.0

install:
	poetry install

run-precommit: ## run pre-commit on all files
	poetry run pre-commit run --all-files

run-datasette: ## run datasette web ui
	poetry run datasette serve \
		--metadata datasette/metadata.json \
		datasette/data.db

run-scrape: ## scrape agencies and towns from directories
	poetry run tracking-gov-pr scrape

run-check-websites: ## run checks on agencies and towns websites
	poetry run tracking-gov-pr check-websites

run-recreate-db: ## recreate sqlite db
	poetry run tracking-gov-pr recreate-db

run: run-scrape run-check-websites run-recreate-db ## scrape, check websites, and recreate db

publish: ## publish datasette to cloudrun
	poetry run datasette publish cloudrun \
		--extra-options="--setting default_cache_ttl 300 --setting sql_time_limit_ms 5000 --setting facet_time_limit_ms 2000" \
		--metadata datasette/metadata.json \
		--install datasette-block-robots \
		--service=tracking-gov-pr \
		datasette/data.db

.PHONY: help
help:
	@grep -E '^[%a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
