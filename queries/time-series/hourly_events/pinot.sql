SELECT
    DATETRUNC('HOUR', event_time) AS hour,
    COUNT(*) AS events,
    SUM(amount) AS total_amount
FROM fact_events
WHERE event_time >= 1748736000000
GROUP BY 1
ORDER BY 1
LIMIT 10000;
