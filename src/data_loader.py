"""
Data Loader Module
Provides functions for loading the Zomato Bangalore dataset into PySpark and Pandas DataFrames.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from src.config import RAW_DATASET_PATH


def load_raw_data_spark(
    spark: SparkSession,
    dataset_path: Optional[Path] = None
) -> DataFrame:
    """
    Loads raw CSV dataset into a PySpark DataFrame with proper multi-line CSV handling.
    """
    path = str(dataset_path or RAW_DATASET_PATH)
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Dataset not found at: {path}. "
            "Please ensure 'zomato.csv' is placed inside 'data/raw/' directory."
        )

    # MultiLine and escape settings are critical for zomato.csv due to embedded newlines in reviews
    df = (
        spark.read
        .option("header", "true")
        .option("multiLine", "true")
        .option("escape", "\"")
        .option("inferSchema", "false")  # Schema is explicitly handled during data cleaning
        .csv(path)
    )
    return df


def load_raw_data_pandas(
    dataset_path: Optional[Path] = None,
    nrows: Optional[int] = None
) -> pd.DataFrame:
    """
    Lightweight Pandas loader for quick exploratory inspection and small samples.
    """
    path = str(dataset_path or RAW_DATASET_PATH)
    if not Path(path).exists():
        raise FileNotFoundError(f"Dataset not found at: {path}")

    return pd.read_csv(path, nrows=nrows, encoding="utf-8")


def get_dataset_dimensions(df: DataFrame) -> Dict[str, Any]:
    """Computes total row count and column count of a Spark DataFrame."""
    return {
        "rows": df.count(),
        "columns": len(df.columns),
        "column_names": df.columns
    }
