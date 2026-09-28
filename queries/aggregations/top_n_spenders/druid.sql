SELECT
    "customer_id",
    SUM("amount") AS total_spend
FROM "sales"
GROUP BY "customer_id"
ORDER BY total_spend DESC
LIMIT 100;
