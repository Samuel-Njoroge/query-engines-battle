SELECT
    c.country,
    SUM(t.amount) AS total_amount
FROM sales t
JOIN customers c
    ON t.customer_id = c.customer_id
GROUP BY c.country;
