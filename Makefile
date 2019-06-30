.PHONY: init
init:
	pip install -r requirements.txt
	sqlite3 afajycal/afajycal.db < db/schema.sql
	sqlite3 tests/afajycal_test.db < db/schema.sql
