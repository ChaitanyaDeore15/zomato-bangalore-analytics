"""
Unit Tests for Spark Analysis and Aggregation Logic
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.spark_session import get_spark_session, stop_spark_session
from src.spark_analysis import (
    analyze_localities,
    analyze_cuisines_popularity,
    analyze_cuisine_ratings_with_threshold,
    analyze_online_order_impact
)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType


@pytest.fixture(scope="session")
def spark():
    session = get_spark_session("Zomato_AnalysisTests")
    yield session
    stop_spark_session(session)


@pytest.fixture
def synthetic_df(spark):
    """Synthetic test fixture with controlled values."""
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("location", StringType(), True),
        StructField("cuisines", StringType(), True),
        StructField("rating_num", DoubleType(), True),
        StructField("approx_cost_num", DoubleType(), True),
        StructField("votes_num", IntegerType(), True),
        StructField("online_order", StringType(), True),
        StructField("book_table", StringType(), True)
    ])
    data = [
        ("Rest 1", "BTM", "North Indian, Chinese", 4.0, 500.0, 100, "Yes", "No"),
        ("Rest 2", "BTM", "South Indian", 3.8, 300.0, 50, "Yes", "No"),
        ("Rest 3", "BTM", "North Indian", 4.2, 600.0, 200, "No", "No"),
        ("Rest 4", "Koramangala", "Continental, Italian", 4.5, 1200.0, 500, "Yes", "Yes"),
        ("Rest 5", "Koramangala", "Chinese", 3.5, 400.0, 80, "No", "No")
    ]
    return spark.createDataFrame(data, schema)


def test_analyze_localities(synthetic_df):
    """Verifies locality grouping and restaurant counts."""
    res = analyze_localities(synthetic_df).collect()
    counts = {row["location"]: row["restaurant_count"] for row in res}
    assert counts["BTM"] == 3
    assert counts["Koramangala"] == 2


def test_analyze_cuisines_popularity(synthetic_df):
    """Verifies that cuisines are exploded properly."""
    res = analyze_cuisines_popularity(synthetic_df).collect()
    counts = {row["cuisine_item"]: row["restaurant_count"] for row in res}
    assert counts["North Indian"] == 2
    assert counts["Chinese"] == 2
    assert counts["South Indian"] == 1
    assert counts["Continental"] == 1


def test_sample_size_thresholding(synthetic_df):
    """Verifies threshold filtering excludes categories below min_restaurants."""
    # With min_restaurants=2, only North Indian and Chinese should be present
    res = analyze_cuisine_ratings_with_threshold(synthetic_df, min_restaurants=2).collect()
    cuisines = [row["cuisine_item"] for row in res]
    assert "North Indian" in cuisines
    assert "Chinese" in cuisines
    assert "Continental" not in cuisines  # Count is only 1, so excluded


def test_online_order_impact(synthetic_df):
    """Verifies calculation of online order segment comparison."""
    res = analyze_online_order_impact(synthetic_df).collect()
    mapping = {row["online_order"]: row["restaurant_count"] for row in res}
    assert mapping["Yes"] == 3
    assert mapping["No"] == 2
