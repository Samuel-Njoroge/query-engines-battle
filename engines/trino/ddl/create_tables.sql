-- Run once after `python scripts/upload_to_s3.py` has copied the generated
-- dataset into Garage (S3-compatible), e.g.:
--   docker compose --profile trino exec trino trino --file /dev/stdin < engines/trino/ddl/create_tables.sql
--
-- Replace ${SCALE} with the scale tier used for datagen (tiny/small/medium/large).

CREATE SCHEMA IF NOT EXISTS hive.benchmark
WITH (location = 's3a://benchmark-data/${SCALE}/');

CREATE TABLE IF NOT EXISTS hive.benchmark.customers (
    customer_id   BIGINT,
    name          VARCHAR,
    country       VARCHAR,
    segment       VARCHAR,
    signup_date   DATE
)
WITH (
    external_location = 's3a://benchmark-data/${SCALE}/customers/',
    format = 'PARQUET'
);

CREATE TABLE IF NOT EXISTS hive.benchmark.products (
    product_id    BIGINT,
    name          VARCHAR,
    category      VARCHAR,
    sub_category  VARCHAR,
    unit_price    DOUBLE
)
WITH (
    external_location = 's3a://benchmark-data/${SCALE}/products/',
    format = 'PARQUET'
);

CREATE TABLE IF NOT EXISTS hive.benchmark.sales (
    sale_id         BIGINT,
    customer_id     BIGINT,
    product_id      BIGINT,
    sale_timestamp  TIMESTAMP,
    quantity        INTEGER,
    amount          DOUBLE,
    sale_date       DATE
)
WITH (
    external_location = 's3a://benchmark-data/${SCALE}/sales/',
    format = 'PARQUET',
    partitioned_by = ARRAY['sale_date']
);

CREATE TABLE IF NOT EXISTS hive.benchmark.fact_events (
    event_id      BIGINT,
    customer_id   BIGINT,
    event_time    TIMESTAMP,
    country       VARCHAR,
    event_type    VARCHAR,
    amount        DOUBLE,
    event_date    DATE
)
WITH (
    external_location = 's3a://benchmark-data/${SCALE}/fact_events/',
    format = 'PARQUET',
    partitioned_by = ARRAY['event_date']
);

-- Hive-partitioned directories (event_date=YYYY-MM-DD/...) need to be registered
-- explicitly so Trino's optimizer can do partition pruning:
CALL hive.system.sync_partition_metadata('benchmark', 'sales', 'ADD');
CALL hive.system.sync_partition_metadata('benchmark', 'fact_events', 'ADD');
