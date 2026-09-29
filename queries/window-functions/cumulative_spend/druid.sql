-- Requires Druid 28+ with the `enableWindowing` query context flag set to true.
SELECT
    "customer_id",
    "sale_date",
    "amount",
    SUM("amount") OVER (
        PARTITION BY "customer_id"
        ORDER BY "sale_date"
    ) AS cumulative_spend
FROM "sales";
