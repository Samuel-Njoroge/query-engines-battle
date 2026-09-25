LOAD LABEL benchmark.load_customers_${SCALE}
(
    DATA INFILE("s3://benchmark-data/${SCALE}/customers/*.parquet")
    INTO TABLE customers
    FORMAT AS "parquet"
)
WITH S3
(
    "provider" = "S3",
    "s3.endpoint" = "http://garage:3900",
    "s3.region" = "us-east-1",
    "s3.access_key" = "GK86b64fdb0310ad7397228be5",
    "s3.secret_key" = "4d1395f9529c8e8b9a7f61d1d31bf46714e30fa1a03ee1600c5b1ba599c131b2"
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
    "provider" = "S3",
    "s3.endpoint" = "http://garage:3900",
    "s3.region" = "us-east-1",
    "s3.access_key" = "GK86b64fdb0310ad7397228be5",
    "s3.secret_key" = "4d1395f9529c8e8b9a7f61d1d31bf46714e30fa1a03ee1600c5b1ba599c131b2"
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
    "provider" = "S3",
    "s3.endpoint" = "http://garage:3900",
    "s3.region" = "us-east-1",
    "s3.access_key" = "GK86b64fdb0310ad7397228be5",
    "s3.secret_key" = "4d1395f9529c8e8b9a7f61d1d31bf46714e30fa1a03ee1600c5b1ba599c131b2"
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
    "provider" = "S3",
    "s3.endpoint" = "http://garage:3900",
    "s3.region" = "us-east-1",
    "s3.access_key" = "GK86b64fdb0310ad7397228be5",
    "s3.secret_key" = "4d1395f9529c8e8b9a7f61d1d31bf46714e30fa1a03ee1600c5b1ba599c131b2"
)
PROPERTIES ("timeout" = "7200");

