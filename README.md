# The Query Engines Battle

A performance comparison of five analytical query engines using a common dataset, workload, and execution environment.

## 1. Background

**The Query Engines Battle** is a benchmarking project comparing the performance and resource characteristics of:

* **Trino**
* **Apache Doris**
* **Apache Drill**
* **Apache Pinot**
* **Apache Druid**

The engines are evaluated using the same datasets and equivalent analytical workloads.

The objective is to understand how these engines behave under different query patterns rather than simply identifying a single "fastest" engine.

## 2. Why?

The project originates from a real-world data-platform scenario requiring both **Trino** and **Apache Doris** usage.

This raised a broader question:

> **How do Trino and Apache Doris compare with other analytical query engines under the same workloads?**

That curiosity led to this benchmark.

Rather than relying solely on vendor documentation or published benchmarks, the project provides a controlled environment where the five engines can be tested against the same data and queries.

The benchmark aims to explore differences in:

* Query execution performance
* Data scanning efficiency
* Aggregation performance
* Join performance
* Filtering performance
* Resource consumption
* Performance as data volume increases
* Behaviour across different analytical workloads

## 3. Query Engines

The benchmark focuses exclusively on five engines.

Each engine is evaluated independently using equivalent workloads wherever the engine supports the required functionality.

| Engine           | Primary Focus                                                                                 |
| ---------------- | --------------------------------------------------------------------------------------------- |
| **Trino**        | Distributed SQL query engine for querying data across heterogeneous sources                   |
| **Apache Doris** | MPP analytical database designed for real-time and interactive analytics                      |
| **Apache Drill** | Distributed SQL query engine designed for querying diverse data sources                       |
| **Apache Pinot** | Distributed real-time OLAP datastore optimized for low-latency analytics                      |
| **Apache Druid** | Distributed analytical data store optimized for fast aggregations and time-oriented workloads |


## 4. Benchmark Dataset

A common dataset is used across all five engines to ensure that the benchmark compares query engines rather than differences in the underlying data.

The dataset contains characteristics representative of analytical workloads, including:

* Large fact tables
* Dimension attributes
* Numerical measures
* High-cardinality columns
* Low-cardinality columns
* Timestamp/date fields
* Repeated values
* Data suitable for filtering, aggregation and joins

### Dataset characteristics

The benchmark documents:

* Number of rows
* Number of columns
* Dataset size
* Data types
* Cardinality
* Distribution of values
* Number of partitions/segments
* Storage format

For example:

```text
Small
├── ~10 million rows

Medium
├── ~100 million rows

Large
└── ~1 billion+ rows
```

## 5. Test Environment

To make the results meaningful, all engines will are tested using a controlled environment.

The benchmark documents:

### Hardware

* CPU
* Number of cores
* RAM
* Storage type
* Storage capacity
* Network configuration

### Software

* Operating system
* Engine version
* Java version
* Docker version
* Dataset version
* Configuration parameters

### Infrastructure

Each engine runs in an isolated environment with documented resource allocations.

The goal is to minimize environmental differences that could influence query performance.

## 6. Workloads

The benchmark uses a common set of analytical workloads.

Queries are designed to represent realistic data-platform use cases.

### 6.1 Full Table Scan

Measures the ability of an engine to scan large volumes of data.

Example:

```sql
SELECT COUNT(*)
FROM fact_events;
```

### 6.2 Filtering

Tests predicate evaluation and data skipping/filter pushdown.

Example:

```sql
SELECT COUNT(*)
FROM fact_events
WHERE event_date >= DATE '2026-01-01'
  AND country = 'KE';
```

### 6.3 Aggregation

Tests grouped analytical queries.

Example:

```sql
SELECT
    country,
    COUNT(*) AS events,
    SUM(amount) AS total_amount
FROM fact_events
GROUP BY country;
```

### 6.4 High-Cardinality Aggregation

Tests aggregation performance when grouping by a column with many distinct values.

Example:

```sql
SELECT
    customer_id,
    COUNT(*) AS transactions,
    SUM(amount) AS total_amount
FROM transactions
GROUP BY customer_id;
```

### 6.5 Join

Tests distributed join performance.

Example:

```sql
SELECT
    c.country,
    SUM(t.amount) AS total_amount
FROM transactions t
JOIN customers c
    ON t.customer_id = c.customer_id
GROUP BY c.country;
```

### 6.6 Multi-Join Analytical Query

Tests more complex analytical workloads involving multiple tables.

Example:

```sql
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
```

### 6.7 Time-Series Query

Particularly relevant for engines designed around analytical and time-oriented workloads.

Example:

```sql
SELECT
    DATE_TRUNC('hour', event_time) AS hour,
    COUNT(*) AS events,
    SUM(amount) AS total_amount
FROM events
WHERE event_time >= TIMESTAMP '2026-01-01 00:00:00'
GROUP BY 1
ORDER BY 1;
```

### 6.8 Top-N

Tests sorting, aggregation and ranking.

Example:

```sql
SELECT
    customer_id,
    SUM(amount) AS total_spend
FROM transactions
GROUP BY customer_id
ORDER BY total_spend DESC
LIMIT 100;
```

### 6.9 Window Functions

Tests more advanced analytical processing.

Example:

```sql
SELECT
    customer_id,
    transaction_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
        ORDER BY transaction_date
    ) AS cumulative_spend
FROM transactions;
```

Where an engine does not support an equivalent operation, that limitation is documented rather than forcing an artificial comparison.

## 7. Benchmark Methodology

The benchmark follows a consistent methodology across all five engines.

### 7.1 Query Execution

Each query is executed multiple times.

For example:

```text
Warm-up runs
├── Run 1
├── Run 2

Measured runs
├── Run 3
├── Run 4
├── Run 5
├── Run 6
└── Run 7
```

Warm-up executions are not included in the final measurements.

This helps separate initial startup/cache effects from steady-state performance.

### 7.2 Metrics

The benchmark captures more than execution time.

### Performance

* Query execution time
* Planning time
* Execution time
* Throughput
* Rows processed
* Rows returned
* Bytes scanned

### Resource consumption

* CPU utilization
* Peak memory
* Average memory
* Disk I/O
* Network I/O

### Scaling

The benchmark also evaluates how performance changes as the dataset grows.

For example:

```text
10M rows
     ↓
100M rows
     ↓
1B rows
```

### 7.3 Repetitions

Each benchmark query is executed multiple times.

The results capture:

```text
minimum
maximum
mean
median
p95
standard deviation
```

### 7.4 Fairness

The benchmark attempts to keep the comparison fair by maintaining consistent:

* Hardware
* Dataset
* Query logic
* Data volume
* Resource limits
* Number of executions
* Measurement methodology

Engine-specific optimizations are documented rather than hidden.

For example, if an engine requires a particular indexing, partitioning, sorting or ingestion strategy to perform efficiently, that configuration is explicitly documented.

## 8. Results

Results are collected automatically and stored in a structured format.

A result record could look like:

```json
{
  "engine": "trino",
  "query": "aggregation_01",
  "dataset_size": "100M",
  "run": 5,
  "execution_time_ms": 842,
  "rows_processed": 100000000,
  "bytes_scanned": 18400000000,
  "peak_memory_mb": 4210
}
```

Results will then be used to generate comparisons such as:

* Execution time by engine
* Query latency distribution
* Throughput
* Memory consumption
* CPU utilization
* Performance by workload
* Performance by dataset size

## 9. Analysis

The analysis focus on **why** performance differs between engines.

Rather than presenting only a leaderboard, the benchmark investigates the underlying behaviour.

Questions include:

### Query execution

* How does each engine execute large scans?
* How efficiently does it perform aggregations?
* How does it handle joins?
* How effective are filtering and predicate pushdown?

### Storage and indexing

* How does the storage architecture affect performance?
* How do partitioning and indexing influence query execution?
* How does segment-oriented storage affect analytical workloads?

### Distributed execution

* How does performance change as data volume increases?
* How much overhead does distributed execution introduce?
* How does each engine utilize available CPU and memory?

### Workload characteristics

* Which workloads favour each engine?
* How does workload type affect relative performance?
* Does an engine optimized for one workload behave differently on another?

The analysis distinguishes between **measured benchmark results** and interpretations about why those results occurred.

## 10. Conclusions

The final analysis answers questions such as:

* Where does Trino perform well?
* Where does Apache Doris perform well?
* Where does Apache Drill perform well?
* Where does Apache Pinot perform well?
* Where does Apache Druid perform well?
* What trade-offs exist between the engines?
* How does workload type influence the results?
* How does data volume affect the results?
* What resource characteristics accompany the observed performance?

## 11. Reproducing the Benchmark

The repository structure:

```text
query-engines-battle/
│
├── engines/
│   ├── trino/
│   ├── doris/
│   ├── drill/
│   ├── pinot/
│   └── druid/
│
├── datasets/
│
├── queries/
│   ├── scans/
│   ├── filters/
│   ├── aggregations/
│   ├── joins/
│   ├── time_series/
│   └── window_functions/
│
├── benchmark/
│   ├── runner/
│   ├── metrics/
│   └── reports/
│
├── results/
│
├── docker-compose.yml
│
└── README.md
```
