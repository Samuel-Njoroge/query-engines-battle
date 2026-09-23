"""Table schemas and scale-tier definitions for the shared benchmark dataset.

Every engine (Trino, Doris, Drill, Pinot, Druid) is loaded from the same generated
Parquet files, so the schema and row counts defined here are the single source of
truth for the whole benchmark.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Countries kept deliberately small so `country` behaves as a low-cardinality
# grouping/filtering column, as described in README section 4.
COUNTRIES = [
    "KE", "NG", "ZA", "EG", "GH", "US", "GB", "DE", "FR", "IN",
    "CN", "JP", "BR", "MX", "CA", "AU", "AE", "SA", "PL", "NL",
]

PRODUCT_CATEGORIES = {
    "Electronics": ["Phones", "Laptops", "Accessories", "Audio"],
    "Home": ["Kitchen", "Furniture", "Decor", "Garden"],
    "Fashion": ["Menswear", "Womenswear", "Footwear", "Accessories"],
    "Grocery": ["Beverages", "Snacks", "Produce", "Dairy"],
    "Sports": ["Fitness", "Outdoor", "Team Sports", "Cycling"],
}

EVENT_TYPES = ["page_view", "add_to_cart", "checkout", "purchase", "refund", "login"]

CUSTOMER_SEGMENTS = ["consumer", "small_business", "enterprise"]

# Row counts per scale tier, keyed by fact table. `tiny` is the default used for
# local development/testing; `small`/`medium`/`large` map to README section 4's
# published tiers.
SCALE_TIERS: dict[str, int] = {
    "tiny": 1_000_000,
    "small": 10_000_000,
    "medium": 100_000_000,
    "large": 1_000_000_000,
}

PRODUCTS_ROW_COUNT = 2_000
# Number of dimension rows scales with the fact tables but is capped so it stays
# a genuinely low/medium-cardinality dimension even at the "large" tier.
CUSTOMERS_ROW_COUNT_DIVISOR = 100
CUSTOMERS_ROW_COUNT_CAP = 5_000_000

DATASET_START_DATE = "2025-01-01"
DATASET_END_DATE = "2026-01-01"


@dataclass(frozen=True)
class Column:
    name: str
    dtype: str  # pandas/pyarrow dtype string
    description: str = ""


@dataclass(frozen=True)
class TableSchema:
    name: str
    columns: list[Column]
    partition_column: str | None = None
    description: str = ""


CUSTOMERS = TableSchema(
    name="customers",
    description="Dimension table: one row per customer.",
    columns=[
        Column("customer_id", "int64", "Primary key, high cardinality"),
        Column("name", "string"),
        Column("country", "string", "Low cardinality, joins to fact tables"),
        Column("segment", "string", "consumer / small_business / enterprise"),
        Column("signup_date", "date32[day]"),
    ],
)

PRODUCTS = TableSchema(
    name="products",
    description="Dimension table: one row per product.",
    columns=[
        Column("product_id", "int64", "Primary key"),
        Column("name", "string"),
        Column("category", "string", "Low cardinality"),
        Column("sub_category", "string", "Medium cardinality"),
        Column("unit_price", "float64"),
    ],
)

SALES = TableSchema(
    name="sales",
    description=(
        "Fact table used for aggregation, high-cardinality aggregation, join, "
        "multi-join, top-n and window-function workloads."
    ),
    partition_column="sale_date",
    columns=[
        Column("sale_id", "int64", "Primary key, high cardinality"),
        Column("customer_id", "int64", "FK -> customers"),
        Column("product_id", "int64", "FK -> products"),
        Column("sale_date", "date32[day]", "Partition column"),
        Column("sale_timestamp", "timestamp[us]"),
        Column("quantity", "int32"),
        Column("amount", "float64"),
    ],
)

FACT_EVENTS = TableSchema(
    name="fact_events",
    description="Fact table used for full-scan, filter and time-series workloads.",
    partition_column="event_date",
    columns=[
        Column("event_id", "int64", "Primary key, high cardinality"),
        Column("customer_id", "int64", "FK -> customers"),
        Column("event_time", "timestamp[us]"),
        Column("event_date", "date32[day]", "Partition column"),
        Column("country", "string", "Low cardinality"),
        Column("event_type", "string", "Low cardinality"),
        Column("amount", "float64", "0 for non-purchase event types"),
    ],
)

ALL_TABLES: list[TableSchema] = [CUSTOMERS, PRODUCTS, SALES, FACT_EVENTS]


def fact_row_count(scale: str) -> int:
    if scale not in SCALE_TIERS:
        raise ValueError(f"Unknown scale '{scale}'. Expected one of {list(SCALE_TIERS)}")
    return SCALE_TIERS[scale]


def customers_row_count(scale: str) -> int:
    return min(fact_row_count(scale) // CUSTOMERS_ROW_COUNT_DIVISOR + 1, CUSTOMERS_ROW_COUNT_CAP)
