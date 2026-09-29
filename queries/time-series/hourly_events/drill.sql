SELECT
    DATE_TRUNC('HOUR', event_time) AS `hour`,
    COUNT(*) AS events,
    SUM(amount) AS total_amount
FROM dfs.bench.`fact_events`
WHERE event_time >= TIMESTAMP '2025-06-01 00:00:00'
GROUP BY 1
ORDER BY 1;
