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
makemigrations_auth:
	@read -p "Enter migration message: " MSG; \
	docker exec movies_auth alembic revision --autogenerate -m "$$MSG"

.PHONY: migrate_auth
migrate_auth:
	docker exec movies_auth alembic upgrade head

.PHONY: load_movies
load_movies:
	docker exec movies_django python manage.py loaddata movies_data.json

.PHONY: create_admin
create_admin:
	@read -p "Enter username: " USERNAME; \
	 read -p "Enter password: " PASSWORD; \
	 read -p "Enter first name: " FIRST_NAME; \
	 read -p "Enter last name: " LAST_NAME; \
	 read -p "Enter email: " EMAIL; \
	 docker exec movies_auth python cli/create_superuser_cli.py "$$USERNAME" "$$PASSWORD" "$$FIRST_NAME" "$$LAST_NAME" "$$EMAIL"
