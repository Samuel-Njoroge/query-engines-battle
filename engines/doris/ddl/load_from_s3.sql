LOAD LABEL benchmark.load_customers_${SCALE}
(
    DATA INFILE("s3://benchmark-data/${SCALE}/customers/*.parquet")
    INTO TABLE customers
    FORMAT AS "parquet"
)
WITH S3
(
    "provider" = "MINIO",
    "s3.endpoint" = "http://minio:9000",
    "s3.region" = "us-east-1",
    "s3.access_key" = "minioadmin",
    "s3.secret_key" = "minioadmin"
)
PROPERTIES ("timeout" = "3600");

LOAD LABEL benchmark.load_products_${SCALE}
(
    DATA INFILE("s3://benchmark-data/${SCALE}/products/*.parquet")
    INTO TABLE products
    FORMAT AS "parquet"
)
WITH S3
(
    "provider" = "MINIO",
    "s3.endpoint" = "http://minio:9000",
    "s3.region" = "us-east-1",
    "s3.access_key" = "minioadmin",
    "s3.secret_key" = "minioadmin"
)
PROPERTIES ("timeout" = "3600");

LOAD LABEL benchmark.load_sales_${SCALE}
(
    DATA INFILE("s3://benchmark-data/${SCALE}/sales/*/*.parquet")
    INTO TABLE sales
    FORMAT AS "parquet"
    (sale_id, customer_id, product_id, sale_timestamp, quantity, amount)
    COLUMNS FROM PATH AS (sale_date)
)
WITH S3
(
    "provider" = "MINIO",
    "s3.endpoint" = "http://minio:9000",
    "s3.region" = "us-east-1",
    "s3.access_key" = "minioadmin",
    "s3.secret_key" = "minioadmin"
)
PROPERTIES ("timeout" = "7200");

LOAD LABEL benchmark.load_fact_events_${SCALE}
(
    DATA INFILE("s3://benchmark-data/${SCALE}/fact_events/*/*.parquet")
    INTO TABLE fact_events
    FORMAT AS "parquet"
    (event_id, customer_id, event_time, country, event_type, amount)
    COLUMNS FROM PATH AS (event_date)
)
WITH S3
(
    "provider" = "MINIO",
    "s3.endpoint" = "http://minio:9000",
    "s3.region" = "us-east-1",
    "s3.access_key" = "minioadmin",
    "s3.secret_key" = "minioadmin"
)
PROPERTIES ("timeout" = "7200");

