run:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	pylint app/ tests/
	black --check app/ tests/

format:
	black app/ tests/
