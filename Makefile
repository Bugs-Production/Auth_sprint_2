.PHONY: build
build:
	docker-compose build

.PHONY: start
start:
	docker-compose up -d

.PHONY: stop
stop:
	docker-compose down

.PHONY: makemigrations_auth
makemigrations:
	@read -p "Enter migration message: " MSG; \
	docker exec movies_auth alembic revision --autogenerate -m "$$MSG"

.PHONY: migrate_auth
migrate:
	docker exec movies_auth alembic upgrade head
