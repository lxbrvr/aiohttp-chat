dev:
	docker-compose up --build

populate_db:
	docker-compose run --rm backend python src/cli.py populate_db

clean_db:
	docker-compose run --rm backend python src/cli.py clean_db
