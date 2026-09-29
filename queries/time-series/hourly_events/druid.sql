SELECT
    TIME_FLOOR(__time, 'PT1H') AS "hour",
    COUNT(*) AS events,
    SUM("amount") AS total_amount
FROM "fact_events"
WHERE __time >= TIMESTAMP '2025-06-01 00:00:00'
GROUP BY 1
ORDER BY 1;
