.PHONY: install run test test-api test-ui performance

install:
	python3 -m pip install -r requirements-dev.txt

run:
	python3 run.py

test:
	python3 -m pytest

test-api:
	python3 -m pytest -m "not ui"

test-ui:
	python3 -m pytest -m ui

performance:
	locust -f performance/locustfile.py --host http://127.0.0.1:5000

