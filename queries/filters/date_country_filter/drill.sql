SELECT COUNT(*)
FROM dfs.bench.`fact_events`
WHERE event_date >= DATE '2025-06-01'
  AND country = 'KE';
