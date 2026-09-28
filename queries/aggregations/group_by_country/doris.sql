SELECT
    country,
    COUNT(*) AS events,
    SUM(amount) AS total_amount
FROM fact_events
GROUP BY country;
