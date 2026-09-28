SELECT
    "customer_id",
    COUNT(*) AS transactions,
    SUM("amount") AS total_amount
FROM "sales"
GROUP BY "customer_id";
