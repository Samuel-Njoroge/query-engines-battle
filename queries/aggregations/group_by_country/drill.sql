SELECT
    country,
    COUNT(*) AS events,
    SUM(amount) AS total_amount
FROM dfs.bench.`fact_events`
GROUP BY country;
