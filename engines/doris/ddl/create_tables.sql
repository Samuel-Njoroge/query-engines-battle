-- Run via: docker compose --profile doris exec doris-fe mysql -h127.0.0.1 -P9030 -uroot < engines/doris/ddl/create_tables.sql
CREATE DATABASE IF NOT EXISTS benchmark;
USE benchmark;

CREATE TABLE IF NOT EXISTS customers (
    customer_id   BIGINT,
    name          VARCHAR(64),
    country       VARCHAR(8),
    segment       VARCHAR(32),
    signup_date   DATE
)
DUPLICATE KEY(customer_id)
DISTRIBUTED BY HASH(customer_id) BUCKETS 8
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS products (
    product_id    BIGINT,
    name          VARCHAR(64),
    category      VARCHAR(32),
    sub_category  VARCHAR(32),
    unit_price    DOUBLE
)
DUPLICATE KEY(product_id)
DISTRIBUTED BY HASH(product_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS sales (
    sale_id         BIGINT,
    customer_id     BIGINT,
    product_id      BIGINT,
    sale_date       DATE,
    sale_timestamp  DATETIME,
    quantity        INT,
    amount          DOUBLE
)
DUPLICATE KEY(sale_id, customer_id)
PARTITION BY RANGE(sale_date) ()
DISTRIBUTED BY HASH(customer_id) BUCKETS 16
PROPERTIES (
    "replication_num" = "1",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "MONTH",
    "dynamic_partition.start" = "-24",
    "dynamic_partition.end" = "3",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "16"
);

CREATE TABLE IF NOT EXISTS fact_events (
    event_id      BIGINT,
    customer_id   BIGINT,
    event_time    DATETIME,
    event_date    DATE,
    country       VARCHAR(8),
    event_type    VARCHAR(32),
    amount        DOUBLE
)
DUPLICATE KEY(event_id, customer_id)
PARTITION BY RANGE(event_date) ()
DISTRIBUTED BY HASH(customer_id) BUCKETS 16
PROPERTIES (
    "replication_num" = "1",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "MONTH",
    "dynamic_partition.start" = "-24",
    "dynamic_partition.end" = "3",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "16"
);
