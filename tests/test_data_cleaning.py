"""
Unit Tests for Data Cleaning and Preprocessing Pipeline
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.spark_session import get_spark_session, stop_spark_session
from src.data_cleaning import (
    clean_rating_column,
    clean_cost_column,
    clean_votes_column,
    normalize_categoricals,
    deduplicate_restaurants,
    clean_dataset_spark
)
from pyspark.sql.types import StructType, StructField, StringType, IntegerType


@pytest.fixture(scope="session")
def spark():
    session = get_spark_session("Zomato_UnitTests")
    yield session
    stop_spark_session(session)


def test_rating_parsing_and_null_handling(spark):
    """Verifies that '4.1/5' is parsed to 4.1, and 'NEW', '-', null are converted to null."""
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("rate", StringType(), True)
    ])
    test_data = [
        ("Cafe A", "4.1/5"),
        ("Cafe B", "NEW"),
        ("Cafe C", "-"),
        ("Cafe D", None),
        ("Cafe E", "3.8/5")
    ]
    df = spark.createDataFrame(test_data, schema)
    result = clean_rating_column(df).collect()

    rates = {row["name"]: row["rating_num"] for row in result}
    assert rates["Cafe A"] == pytest.approx(4.1)
    assert rates["Cafe B"] is None  # Must NOT be 0.0
    assert rates["Cafe C"] is None  # Must NOT be 0.0
    assert rates["Cafe D"] is None
    assert rates["Cafe E"] == pytest.approx(3.8)


def test_cost_parsing_with_commas(spark):
    """Verifies that commas are stripped and converted to numeric Double."""
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("approx_cost(for two people)", StringType(), True)
    ])
    test_data = [
        ("Rest A", "800"),
        ("Rest B", "1,200"),
        ("Rest C", "2,500"),
        ("Rest D", None),
        ("Rest E", "")
    ]
    df = spark.createDataFrame(test_data, schema)
    result = clean_cost_column(df).collect()

    costs = {row["name"]: row["approx_cost_num"] for row in result}
    assert costs["Rest A"] == pytest.approx(800.0)
    assert costs["Rest B"] == pytest.approx(1200.0)
    assert costs["Rest C"] == pytest.approx(2500.0)
    assert costs["Rest D"] is None
    assert costs["Rest E"] is None


def test_votes_parsing(spark):
    """Verifies votes are cast to integer and nulls become 0."""
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("votes", StringType(), True)
    ])
    test_data = [
        ("Rest A", "775"),
        ("Rest B", "0"),
        ("Rest C", None)
    ]
    df = spark.createDataFrame(test_data, schema)
    result = clean_votes_column(df).collect()

    votes = {row["name"]: row["votes_num"] for row in result}
    assert votes["Rest A"] == 775
    assert votes["Rest B"] == 0
    assert votes["Rest C"] == 0


def test_entity_deduplication(spark):
    """Verifies deduplication on physical identity [name, address, location]."""
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("address", StringType(), True),
        StructField("location", StringType(), True),
        StructField("listed_in(city)", StringType(), True)
    ])
    test_data = [
        ("Chai Point", "100 Indiranagar", "Indiranagar", "Indiranagar"),
        ("Chai Point", "100 Indiranagar", "Indiranagar", "Old Airport Road"),  # Duplicate listing
        ("Chai Point", "200 Koramangala", "Koramangala", "Koramangala")       # Different branch
    ]
    df = spark.createDataFrame(test_data, schema)
    deduped_df, dropped_count = deduplicate_restaurants(df)

    assert deduped_df.count() == 2
    assert dropped_count == 1
