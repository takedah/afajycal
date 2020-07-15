.PHONY: init
init:
	pip install -r requirements.txt
	python import_schedules.py
