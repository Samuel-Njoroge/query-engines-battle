SELECT
    c.country,
    p.category,
    SUM(s.amount) AS revenue,
    COUNT(*) AS transactions
FROM dfs.bench.`sales` s
JOIN dfs.bench.`customers` c
    ON s.customer_id = c.customer_id
JOIN dfs.bench.`products` p
    ON s.product_id = p.product_id
GROUP BY
    c.country,
    p.category;
