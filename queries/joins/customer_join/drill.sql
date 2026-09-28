SELECT
    c.country,
    SUM(t.amount) AS total_amount
FROM dfs.bench.`sales` t
JOIN dfs.bench.`customers` c
    ON t.customer_id = c.customer_id
GROUP BY c.country;
