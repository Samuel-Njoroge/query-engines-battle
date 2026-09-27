.PHONY: venv datagen up-trino up-doris up-drill up-pinot up-druid down \
        ingest-trino ingest-doris setup-pinot ingest-pinot ingest-druid \
        bench-% report clean

VENV := .venv/bin
SCALE ?= tiny

venv:
	python3 -m venv .venv
	$(VENV)/pip install -q --upgrade pip
	$(VENV)/pip install -q -r requirements.txt

datagen:
	$(VENV)/python datagen/generate.py --scale $(SCALE) --out datasets/

upload:
	$(VENV)/python scripts/upload_to_s3.py --scale $(SCALE)

# --- bring individual engine stacks up/down -------------------------------

up-trino:
	docker compose --profile trino up -d

up-doris:
	docker compose --profile doris up -d

up-drill:
	docker compose --profile drill up -d

up-pinot:
	docker compose --profile pinot up -d

up-druid:
	docker compose --profile druid up -d

down:
	docker compose --profile trino --profile doris --profile drill --profile pinot --profile druid down

# --- one-time ingestion per engine, after `up-<engine>` + `upload` --------

ingest-trino:
	docker compose --profile trino exec -T trino trino --file /dev/stdin < engines/trino/ddl/create_tables.sql

ingest-doris:
	docker compose --profile doris exec -T doris-fe mysql -h127.0.0.1 -P9030 -uroot < engines/doris/ddl/create_tables.sql
	docker compose --profile doris exec -T doris-fe mysql -h127.0.0.1 -P9030 -uroot < engines/doris/ddl/load_from_s3.sql

setup-pinot:
	$(VENV)/python scripts/setup_pinot.py

ingest-pinot: setup-pinot
	docker compose --profile pinot exec pinot-controller bin/pinot-admin.sh LaunchDataIngestionJob -jobSpecFile /opt/pinot/ingestion/fact_events.job.yaml
	docker compose --profile pinot exec pinot-controller bin/pinot-admin.sh LaunchDataIngestionJob -jobSpecFile /opt/pinot/ingestion/sales.job.yaml

ingest-druid:
	$(VENV)/python scripts/submit_druid_ingestion.py --scale $(SCALE) --spec fact_events
	$(VENV)/python scripts/submit_druid_ingestion.py --scale $(SCALE) --spec sales

# --- benchmarking + reporting ----------------------------------------------

# make bench-trino, make bench-doris, ...
bench-%:
	$(VENV)/python -m benchmark.runner.main --engine $* --dataset-size $(SCALE)

report:
	$(VENV)/python -m benchmark.reports.generate_report --dataset-size $(SCALE)

clean:
	rm -rf datasets results benchmark/reports/output
