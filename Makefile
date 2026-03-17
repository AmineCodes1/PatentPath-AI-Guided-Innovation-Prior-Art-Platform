# Development helpers for the PatentPath docker stack.

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

migrate:
	docker compose exec backend alembic upgrade head

test:
	docker compose exec backend pytest -q
