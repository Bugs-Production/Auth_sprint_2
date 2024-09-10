.PHONY: build
build:
	docker-compose build

.PHONY: start
start:
	docker-compose up -d

.PHONY: stop
stop:
	docker-compose down

.PHONY: format
format:
	black . && isort . --skip src/models/__init__.py

.PHONY: makemigrations
makemigrations:
	@read -p "Enter migration message: " MSG; \
	docker exec users_fastapi alembic revision --autogenerate -m "$$MSG"

.PHONY: migrate
migrate:
	docker exec users_fastapi alembic upgrade head

.PHONY: up_test
up_test:
	docker-compose -f docker-compose.test.yml up -d --build

.PHONY: tests
tests:
	docker exec -it auth_fastapi_tests pytest tests -s

.PHONY: down_test
down_test:
	docker-compose -f docker-compose.test.yml down -v
