.PHONY: all
all: lint typecheck test
	@true

.PHONY: test
test:
	docker-compose run --rm --entrypoint=pytest test \
		-m 'not integration' \
		--cov=jira_cli --cov-report term --cov-report html:cov_html \
		--disable-pytest-warnings \
		test/

.PHONY: integration
integration:
	docker-compose run --rm --entrypoint=pytest test \
		-m 'integration' \
		--hostname=locke:8666 \
		--username=blackm \
		--password=eggseggs \
		--cwd=$$(pwd) \
		test/integration

.PHONY: lint
lint:
	docker-compose run --rm --entrypoint=pylint test jira_cli/
	docker-compose run --rm --entrypoint=pylint test --rcfile=test/.pylintrc test/

.PHONY: typecheck
typecheck:
	docker-compose run --rm --entrypoint=pytest test --mypy --mypy-ignore-missing-imports jira_cli/
