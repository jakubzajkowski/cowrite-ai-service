run:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	pylint app/ tests/
	black --check app/ tests/

format:
	black app/ tests/

# Database migrations
migrate:
	alembic revision --autogenerate -m "$(msg)"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

db-history:
	alembic history

db-current:
	alembic current

db-init:
	python -m app.db.migrations
