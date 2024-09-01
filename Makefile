.ONESHELL:

.PHONY: help
help:		## Show this help message.
	@echo "Usage: make <target>"
	@echo "\nTargets:"
	@fgrep "##" Makefile | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/ -/'

.PHONY: requirements
export_requirements:	## Generate the requirements.txt and requirements-dev.txt files.
	poetry export -o requirements.txt --without-hashes
	poetry export -o requirements-dev.txt --with=dev --without-hashes

.PHONY: db_migrate
db_migrate:	## Run the database migrations.
	poetry run python manage.py migrate

.PHONY: db_upgrade
db_upgrade:	## Upgrade the database.
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

.PHONY: db_seed
db_seed:	## Seed the database with initial data.
	poetry run python manage.py seed

.PHONY: db_purge
db_purge:	## Purge the database.
	poetry run python manage.py flush

.PHONY: run
run:		## Run the development server.
	poetry run python manage.py runserver --nostatic

.PHONY: seed
seed:		## Seed the database with initial data.
	poetry run python manage.py seed

.PHONY: shell
shell:		## Run the Django shell.
	poetry run python manage.py shell

.PHONY: tailwind
tailwind:	## Compile the Tailwind CSS.
	npx tailwindcss -i app/static/src/input.css -o app/static/src/tailwind.css --watch