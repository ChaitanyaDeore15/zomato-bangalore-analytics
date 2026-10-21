"""
Data Cleaning and Preprocessing Module
Implements Spark transformations for cleaning raw Zomato records:
- Parsing ratings (handling '4.1/5', 'NEW', '-', None)
- Formatting approximate cost (handling thousand commas)
- Type casting votes to Integer
- Categorical whitespace normalization
- Deduplication and data quality auditing
"""

from typing import Tuple, Dict, Any
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, StringType
from src.config import (
    COL_NAME, COL_ADDRESS, COL_LOCATION, COL_ONLINE_ORDER, COL_BOOK_TABLE,
    COL_RATE, COL_VOTES, COL_APPROX_COST, COL_CUISINES, COL_REST_TYPE,
    COL_LISTED_IN_TYPE, COL_LISTED_IN_CITY, COL_RATING_NUM,
    COL_APPROX_COST_NUM, COL_VOTES_NUM
)


def clean_rating_column(df: DataFrame) -> DataFrame:
    """
    Cleans the 'rate' column.
    
    Raw values include '4.1/5', 'NEW', '-', and null.
    'NEW', '-', and invalid non-numeric values are converted to null
    rather than 0.0 to prevent severe distortion of statistical distributions.
    """
    # Step 1: Strip whitespace
    cleaned_str = F.trim(F.col(COL_RATE))

    # Step 2: Split by '/' to extract numerator (e.g., '4.1' from '4.1/5')
    extracted_num = F.split(cleaned_str, "/")[0]

    # Step 3: Handle sentinel values ('NEW', '-') and non-numeric strings
    clean_rate_expr = (
        F.when(cleaned_str.isNull(), F.lit(None).cast(DoubleType()))
        .when(cleaned_str.isin(["NEW", "-", ""]), F.lit(None).cast(DoubleType()))
        .otherwise(extracted_num.cast(DoubleType()))
    )

    return df.withColumn(COL_RATING_NUM, clean_rate_expr)


def clean_cost_column(df: DataFrame) -> DataFrame:
    """
    Cleans the approximate cost column by stripping commas (e.g., '1,200' -> 1200.0).
    """
    cost_str = F.regexp_replace(F.trim(F.col(COL_APPROX_COST)), ",", "")
    clean_cost_expr = (
        F.when(cost_str.isNull(), F.lit(None).cast(DoubleType()))
        .when(cost_str == "", F.lit(None).cast(DoubleType()))
        .otherwise(cost_str.cast(DoubleType()))
    )
    return df.withColumn(COL_APPROX_COST_NUM, clean_cost_expr)


def clean_votes_column(df: DataFrame) -> DataFrame:
    """
    Casts votes to IntegerType; replaces null or non-numeric entries with 0.
    """
    clean_votes_expr = (
        F.when(F.col(COL_VOTES).isNull(), F.lit(0))
        .otherwise(F.col(COL_VOTES).cast(IntegerType()))
    )
    return df.withColumn(COL_VOTES_NUM, clean_votes_expr)


def normalize_categoricals(df: DataFrame) -> DataFrame:
    """
    Trims and standardizes key categorical fields.
    """
    normalized_df = (
        df
        .withColumn(COL_NAME, F.trim(F.col(COL_NAME)))
        .withColumn(COL_LOCATION, F.trim(F.col(COL_LOCATION)))
        .withColumn(COL_ONLINE_ORDER, F.initcap(F.trim(F.col(COL_ONLINE_ORDER))))
        .withColumn(COL_BOOK_TABLE, F.initcap(F.trim(F.col(COL_BOOK_TABLE))))
        .withColumn(COL_REST_TYPE, F.trim(F.col(COL_REST_TYPE)))
        .withColumn(COL_CUISINES, F.trim(F.col(COL_CUISINES)))
        .withColumn(COL_LISTED_IN_TYPE, F.trim(F.col(COL_LISTED_IN_TYPE)))
        .withColumn(COL_LISTED_IN_CITY, F.trim(F.col(COL_LISTED_IN_CITY)))
    )
    return normalized_df


def deduplicate_restaurants(df: DataFrame) -> Tuple[DataFrame, int]:
    """
    Deduplicates restaurants based on primary physical identity: [name, address, location].
    
    In the raw dataset, the same restaurant is frequently listed under multiple
    search cities (listed_in(city)). Deduplicating creates an accurate restaurant-level entity.
    """
    initial_count = df.count()
    deduped_df = df.dropDuplicates(subset=[COL_NAME, COL_ADDRESS, COL_LOCATION])
    deduped_count = deduped_df.count()
    dropped_count = initial_count - deduped_count
    return deduped_df, dropped_count


def clean_dataset_spark(
    raw_df: DataFrame,
    deduplicate: bool = True
) -> Tuple[DataFrame, Dict[str, Any]]:
    """
    Runs the complete Spark data cleaning and validation pipeline.
    
    Returns:
        cleaned_df: PySpark DataFrame with normalized columns and parsed numerics.
        quality_report: Dictionary with comprehensive audit metrics.
    """
    initial_rows = raw_df.count()

    # Step 1: Clean numerical features
    df_step1 = clean_rating_column(raw_df)
    df_step2 = clean_cost_column(df_step1)
    df_step3 = clean_votes_column(df_step2)

    # Step 2: Normalize string attributes
    df_step4 = normalize_categoricals(df_step3)

    # Step 3: Filter completely invalid records (null name or null location)
    df_valid = df_step4.filter(
        F.col(COL_NAME).isNotNull() & 
        (F.col(COL_NAME) != "") & 
        F.col(COL_LOCATION).isNotNull() & 
        (F.col(COL_LOCATION) != "")
    )
    valid_rows_before_dedup = df_valid.count()
    dropped_empty_identity = initial_rows - valid_rows_before_dedup

    # Step 4: Optional Deduplication
    if deduplicate:
        cleaned_df, duplicate_count = deduplicate_restaurants(df_valid)
    else:
        cleaned_df = df_valid
        duplicate_count = 0

    final_rows = cleaned_df.count()

    # Compute quality metrics on cleaned dataset
    null_ratings_count = cleaned_df.filter(F.col(COL_RATING_NUM).isNull()).count()
    valid_ratings_count = cleaned_df.filter(F.col(COL_RATING_NUM).isNotNull()).count()
    null_cost_count = cleaned_df.filter(F.col(COL_APPROX_COST_NUM).isNull()).count()
    valid_cost_count = cleaned_df.filter(F.col(COL_APPROX_COST_NUM).isNotNull()).count()

    quality_report = {
        "initial_raw_rows": initial_rows,
        "dropped_missing_identity": dropped_empty_identity,
        "duplicate_rows_removed": duplicate_count,
        "final_cleaned_rows": final_rows,
        "valid_ratings_count": valid_ratings_count,
        "null_or_unrated_count": null_ratings_count,
        "valid_cost_count": valid_cost_count,
        "null_cost_count": null_cost_count,
        "ratings_completeness_pct": round((valid_ratings_count / final_rows) * 100, 2) if final_rows > 0 else 0,
        "cost_completeness_pct": round((valid_cost_count / final_rows) * 100, 2) if final_rows > 0 else 0
    }

    return cleaned_df, quality_report
