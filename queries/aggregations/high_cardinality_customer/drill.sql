SELECT
    customer_id,
    COUNT(*) AS transactions,
    SUM(amount) AS total_amount
FROM dfs.bench.`sales`
GROUP BY customer_id;
