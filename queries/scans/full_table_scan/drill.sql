-- `bench` is the dfs workspace defined in engines/drill/conf/storage-plugins-override.conf,
-- pointed at the Garage/S3 location holding the generated Parquet dataset.
SELECT COUNT(*)
FROM dfs.bench.`fact_events`;
