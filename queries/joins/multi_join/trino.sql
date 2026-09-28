SELECT
    c.country,
    p.category,
    SUM(s.amount) AS revenue,
    COUNT(*) AS transactions
FROM sales s
JOIN customers c
    ON s.customer_id = c.customer_id
JOIN products p
    ON s.product_id = p.product_id
GROUP BY
    c.country,
    p.category;
