SELECT COUNT(*)
FROM "fact_events"
WHERE "event_date" >= TIMESTAMP '2025-06-01 00:00:00'
  AND "country" = 'KE';
