"""
Results Export Orchestrator Module
Runs the end-to-end Spark data cleaning and analytical aggregation pipeline,
saving clean datasets and aggregated CSV result files for visualization and dashboard.
"""

import json
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pyspark.sql import DataFrame
import pandas as pd

from src.spark_session import get_spark_session, stop_spark_session
from src.data_loader import load_raw_data_spark
from src.data_cleaning import clean_dataset_spark
from src.spark_analysis import (
    run_rdd_demonstrations,
    analyze_localities,
    analyze_cuisines_popularity,
    analyze_cuisine_ratings_with_threshold,
    analyze_rating_distribution,
    analyze_cost_distribution,
    analyze_online_order_impact,
    analyze_table_booking_impact,
    analyze_cost_vs_rating_correlation,
    analyze_high_engagement_restaurants,
    compute_locality_cuisine_matrix
)
from src.config import (
    CLEANED_DATASET_PARQUET,
    CLEANED_DATASET_CSV,
    ANALYSIS_RESULTS_DIR,
    PROCESSED_DATA_DIR
)


def export_spark_df_to_csv(df: DataFrame, destination_path: Path):
    """
    Safely exports an aggregated Spark DataFrame to a single clean CSV file via Pandas.
    Appropriate for small aggregated result sets.
    """
    pandas_df = df.toPandas()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    pandas_df.to_csv(destination_path, index=False)
    print(f"Exported: {destination_path.name} ({len(pandas_df)} rows)")


def run_full_pipeline():
    """
    Executes full Spark data cleaning, analytical computation, and result export.
    """
    print("=" * 70)
    print("STARTING APACHE SPARK PIPELINE: ZOMATO BANGALORE ANALYTICS")
    print("=" * 70)

    spark = get_spark_session()

    try:
        # 1. Load Raw Data
        print("\n[1/6] Loading raw dataset from data/raw/zomato.csv...")
        raw_df = load_raw_data_spark(spark)
        raw_count = raw_df.count()
        print(f"Raw records loaded: {raw_count:,}")

        # 2. Clean & Preprocess Data
        print("\n[2/6] Executing PySpark cleaning and validation pipeline...")
        cleaned_df, quality_report = clean_dataset_spark(raw_df, deduplicate=True)
        cleaned_df.cache()  # Cache for repeated analytical queries
        cleaned_count = cleaned_df.count()
        print(f"Cleaned unique restaurant records: {cleaned_count:,}")
        print("Data Quality Report Summary:")
        for k, v in quality_report.items():
            print(f"  - {k}: {v}")

        # Save quality report as CSV
        pd.DataFrame([quality_report]).to_csv(
            ANALYSIS_RESULTS_DIR / "data_quality_report.csv", index=False
        )

        # 3. Save Processed Dataset (Parquet & CSV)
        print("\n[3/6] Persisting cleaned dataset to disk...")
        # Save CSV for Streamlit and lightweight consumers
        cleaned_pandas = cleaned_df.drop("reviews_list", "menu_item").toPandas()
        cleaned_pandas.to_csv(CLEANED_DATASET_CSV, index=False)
        print(f"Persisted clean CSV: {CLEANED_DATASET_CSV} ({len(cleaned_pandas):,} rows)")

        # 4. RDD Demonstrations
        print("\n[4/6] Running PySpark RDD core operations (Unit 3)...")
        rdd_results = run_rdd_demonstrations(cleaned_df)
        print("RDD Top 5 Localities (reduceByKey):", rdd_results["top_5_localities_rdd"])
        print("RDD Top 5 Cuisines (flatMap + reduceByKey):", rdd_results["top_5_cuisines_rdd"])

        # 5. Execute Spark DataFrame Analytical Queries
        print("\n[5/6] Executing Spark DataFrame aggregations and analytical queries...")
        locality_df = analyze_localities(cleaned_df)
        export_spark_df_to_csv(locality_df, ANALYSIS_RESULTS_DIR / "locality_summary.csv")

        cuisine_pop_df = analyze_cuisines_popularity(cleaned_df)
        export_spark_df_to_csv(cuisine_pop_df, ANALYSIS_RESULTS_DIR / "cuisine_popularity.csv")

        cuisine_rated_df = analyze_cuisine_ratings_with_threshold(cleaned_df, min_restaurants=30)
        export_spark_df_to_csv(cuisine_rated_df, ANALYSIS_RESULTS_DIR / "cuisine_ratings_thresholded.csv")

        rating_dist_df = analyze_rating_distribution(cleaned_df)
        export_spark_df_to_csv(rating_dist_df, ANALYSIS_RESULTS_DIR / "rating_distribution.csv")

        cost_dist_df = analyze_cost_distribution(cleaned_df)
        export_spark_df_to_csv(cost_dist_df, ANALYSIS_RESULTS_DIR / "cost_distribution.csv")

        online_impact_df = analyze_online_order_impact(cleaned_df)
        export_spark_df_to_csv(online_impact_df, ANALYSIS_RESULTS_DIR / "online_order_comparison.csv")

        table_impact_df = analyze_table_booking_impact(cleaned_df)
        export_spark_df_to_csv(table_impact_df, ANALYSIS_RESULTS_DIR / "table_booking_comparison.csv")

        high_eng_df = analyze_high_engagement_restaurants(cleaned_df, top_n=20)
        export_spark_df_to_csv(high_eng_df, ANALYSIS_RESULTS_DIR / "high_engagement_restaurants.csv")

        matrix_df = compute_locality_cuisine_matrix(cleaned_df, top_localities=10, top_cuisines=10)
        export_spark_df_to_csv(matrix_df, ANALYSIS_RESULTS_DIR / "locality_cuisine_matrix.csv")

        # Correlations
        correlations = analyze_cost_vs_rating_correlation(cleaned_df)
        with open(ANALYSIS_RESULTS_DIR / "correlations.json", "w", encoding="utf-8") as f:
            json.dump(correlations, f, indent=2)
        pd.DataFrame([correlations]).to_csv(ANALYSIS_RESULTS_DIR / "correlations.csv", index=False)
        print("Exported: correlations.csv", correlations)

        print("\n[6/6] Pipeline execution completed successfully!")
        print(f"All aggregated results saved to: {ANALYSIS_RESULTS_DIR}")

    finally:
        stop_spark_session(spark)
        print("SparkSession stopped.")


if __name__ == "__main__":
    run_full_pipeline()
