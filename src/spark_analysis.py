"""
Spark Analytical Processing Module
Implements all core Big Data analytical queries and RDD operations:
- Locality distributions
- Cuisine tokenization and frequency ranking
- Defensible sample-size thresholded rating aggregations
- Bivariate correlation and segment comparisons
- High-engagement analysis
- Locality-cuisine matrix computation
"""

from typing import Dict, Any, List, Tuple
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.rdd import RDD
from src.config import (
    COL_LOCATION, COL_CUISINES, COL_RATING_NUM, COL_APPROX_COST_NUM,
    COL_VOTES_NUM, COL_ONLINE_ORDER, COL_BOOK_TABLE, COL_NAME,
    MIN_CUISINE_SAMPLE_SIZE, TOP_N_LOCALITIES, TOP_N_CUISINES
)


def run_rdd_demonstrations(df: DataFrame) -> Dict[str, Any]:
    """
    Demonstrates Unit 3 PySpark RDD Core concepts on actual dataset records:
    - RDD creation from DataFrame
    - map() transformation
    - filter() transformation
    - flatMap() transformation (splitting cuisines)
    - reduceByKey() aggregation (restaurant count by locality and cuisine)
    - Actions: count(), take(), collect()
    """
    # Create RDD from DataFrame rows
    rdd = df.rdd

    # Action: count()
    total_rdd_records = rdd.count()

    # Transformation: filter() for records with valid ratings
    filtered_rdd = rdd.filter(lambda row: row[COL_RATING_NUM] is not None)
    rated_count = filtered_rdd.count()

    # Transformation: map() extracting (location, 1) pair RDD
    location_pairs = rdd.filter(lambda row: row[COL_LOCATION] is not None) \
                        .map(lambda row: (row[COL_LOCATION], 1))

    # Transformation: reduceByKey() aggregating total counts per locality
    locality_counts_rdd = location_pairs.reduceByKey(lambda a, b: a + b)
    top_5_localities_rdd = locality_counts_rdd.takeOrdered(5, key=lambda x: -x[1])

    # Transformation: flatMap() to split comma-separated cuisines
    cuisine_rdd = rdd.filter(lambda row: row[COL_CUISINES] is not None) \
                     .flatMap(lambda row: [c.strip() for c in str(row[COL_CUISINES]).split(",") if c.strip()]) \
                     .map(lambda cuisine: (cuisine, 1)) \
                     .reduceByKey(lambda a, b: a + b)
    top_5_cuisines_rdd = cuisine_rdd.takeOrdered(5, key=lambda x: -x[1])

    return {
        "total_rdd_records": total_rdd_records,
        "rated_count": rated_count,
        "top_5_localities_rdd": top_5_localities_rdd,
        "top_5_cuisines_rdd": top_5_cuisines_rdd
    }


def analyze_localities(df: DataFrame, top_n: int = TOP_N_LOCALITIES) -> DataFrame:
    """
    Computes restaurant distribution across Bangalore localities.
    Calculates total restaurants, average rating, and total votes per locality.
    """
    locality_summary = (
        df.filter(F.col(COL_LOCATION).isNotNull() & (F.col(COL_LOCATION) != ""))
        .groupBy(COL_LOCATION)
        .agg(
            F.count(COL_NAME).alias("restaurant_count"),
            F.round(F.avg(COL_RATING_NUM), 2).alias("avg_rating"),
            F.round(F.avg(COL_APPROX_COST_NUM), 2).alias("avg_approx_cost"),
            F.sum(COL_VOTES_NUM).alias("total_votes")
        )
        .orderBy(F.desc("restaurant_count"))
    )
    return locality_summary


def analyze_cuisines_popularity(df: DataFrame, top_n: int = TOP_N_CUISINES) -> DataFrame:
    """
    Tokenizes comma-separated cuisines and calculates individual cuisine frequency and metrics.
    """
    exploded_cuisines = (
        df.filter(F.col(COL_CUISINES).isNotNull() & (F.col(COL_CUISINES) != ""))
        .withColumn("cuisine_item", F.explode(F.split(F.col(COL_CUISINES), r",\s*")))
        .filter(F.col("cuisine_item") != "")
    )

    cuisine_summary = (
        exploded_cuisines
        .groupBy("cuisine_item")
        .agg(
            F.count(COL_NAME).alias("restaurant_count"),
            F.round(F.avg(COL_RATING_NUM), 2).alias("avg_rating"),
            F.round(F.avg(COL_APPROX_COST_NUM), 2).alias("avg_approx_cost"),
            F.sum(COL_VOTES_NUM).alias("total_votes")
        )
        .orderBy(F.desc("restaurant_count"))
    )
    return cuisine_summary


def analyze_cuisine_ratings_with_threshold(
    df: DataFrame,
    min_restaurants: int = MIN_CUISINE_SAMPLE_SIZE
) -> DataFrame:
    """
    Ranks cuisines by average customer rating with a strict minimum sample-size threshold.
    Avoids ranking obscure cuisines with 1 or 2 restaurants as top-rated.
    """
    exploded = (
        df.filter(
            F.col(COL_CUISINES).isNotNull() &
            (F.col(COL_CUISINES) != "") &
            F.col(COL_RATING_NUM).isNotNull()
        )
        .withColumn("cuisine_item", F.explode(F.split(F.col(COL_CUISINES), r",\s*")))
        .filter(F.col("cuisine_item") != "")
    )

    ranked_cuisines = (
        exploded
        .groupBy("cuisine_item")
        .agg(
            F.count(COL_NAME).alias("restaurant_count"),
            F.round(F.avg(COL_RATING_NUM), 2).alias("avg_rating"),
            F.round(F.stddev(COL_RATING_NUM), 2).alias("rating_stddev"),
            F.sum(COL_VOTES_NUM).alias("total_votes")
        )
        .filter(F.col("restaurant_count") >= min_restaurants)
        .orderBy(F.desc("avg_rating"), F.desc("restaurant_count"))
    )
    return ranked_cuisines


def analyze_rating_distribution(df: DataFrame) -> DataFrame:
    """
    Calculates empirical distribution of restaurant ratings in 0.5-point intervals.
    """
    rated_df = df.filter(F.col(COL_RATING_NUM).isNotNull())

    # Create 0.5 bin categories
    distribution = (
        rated_df
        .withColumn(
            "rating_bin",
            F.when(F.col(COL_RATING_NUM) < 2.0, "< 2.0")
            .when((F.col(COL_RATING_NUM) >= 2.0) & (F.col(COL_RATING_NUM) < 2.5), "2.0 - 2.4")
            .when((F.col(COL_RATING_NUM) >= 2.5) & (F.col(COL_RATING_NUM) < 3.0), "2.5 - 2.9")
            .when((F.col(COL_RATING_NUM) >= 3.0) & (F.col(COL_RATING_NUM) < 3.5), "3.0 - 3.4")
            .when((F.col(COL_RATING_NUM) >= 3.5) & (F.col(COL_RATING_NUM) < 4.0), "3.5 - 3.9")
            .when((F.col(COL_RATING_NUM) >= 4.0) & (F.col(COL_RATING_NUM) < 4.5), "4.0 - 4.4")
            .otherwise("4.5 - 5.0")
        )
        .groupBy("rating_bin")
        .agg(
            F.count(COL_NAME).alias("count"),
            F.round(F.avg(COL_VOTES_NUM), 1).alias("avg_votes")
        )
        .orderBy("rating_bin")
    )
    return distribution


def analyze_cost_distribution(df: DataFrame) -> DataFrame:
    """
    Calculates cost tiers for approximate cost for two people.
    """
    cost_df = df.filter(F.col(COL_APPROX_COST_NUM).isNotNull())

    distribution = (
        cost_df
        .withColumn(
            "cost_tier",
            F.when(F.col(COL_APPROX_COST_NUM) <= 300, "Budget (<= ₹300)")
            .when((F.col(COL_APPROX_COST_NUM) > 300) & (F.col(COL_APPROX_COST_NUM) <= 700), "Economy (₹301 - ₹700)")
            .when((F.col(COL_APPROX_COST_NUM) > 700) & (F.col(COL_APPROX_COST_NUM) <= 1500), "Mid-Range (₹701 - ₹1500)")
            .otherwise("Fine Dining (> ₹1500)")
        )
        .groupBy("cost_tier")
        .agg(
            F.count(COL_NAME).alias("restaurant_count"),
            F.round(F.avg(COL_RATING_NUM), 2).alias("avg_rating"),
            F.round(F.avg(COL_VOTES_NUM), 1).alias("avg_votes")
        )
        .orderBy(F.desc("restaurant_count"))
    )
    return distribution


def analyze_online_order_impact(df: DataFrame) -> DataFrame:
    """
    Analyzes differences between restaurants offering online ordering and those that do not.
    """
    return (
        df.filter(F.col(COL_ONLINE_ORDER).isin(["Yes", "No"]))
        .groupBy(COL_ONLINE_ORDER)
        .agg(
            F.count(COL_NAME).alias("restaurant_count"),
            F.round(F.avg(COL_RATING_NUM), 2).alias("avg_rating"),
            F.round(F.avg(COL_APPROX_COST_NUM), 2).alias("avg_approx_cost"),
            F.round(F.avg(COL_VOTES_NUM), 1).alias("avg_votes"),
            F.sum(COL_VOTES_NUM).alias("total_votes")
        )
        .orderBy(COL_ONLINE_ORDER)
    )


def analyze_table_booking_impact(df: DataFrame) -> DataFrame:
    """
    Analyzes differences between restaurants offering table reservations and those that do not.
    """
    return (
        df.filter(F.col(COL_BOOK_TABLE).isin(["Yes", "No"]))
        .groupBy(COL_BOOK_TABLE)
        .agg(
            F.count(COL_NAME).alias("restaurant_count"),
            F.round(F.avg(COL_RATING_NUM), 2).alias("avg_rating"),
            F.round(F.avg(COL_APPROX_COST_NUM), 2).alias("avg_approx_cost"),
            F.round(F.avg(COL_VOTES_NUM), 1).alias("avg_votes"),
            F.sum(COL_VOTES_NUM).alias("total_votes")
        )
        .orderBy(COL_BOOK_TABLE)
    )


def analyze_cost_vs_rating_correlation(df: DataFrame) -> Dict[str, float]:
    """
    Computes Pearson correlation between approximate cost, ratings, and votes.
    """
    valid_df = df.filter(
        F.col(COL_RATING_NUM).isNotNull() & 
        F.col(COL_APPROX_COST_NUM).isNotNull()
    )

    corr_cost_rating = valid_df.stat.corr(COL_APPROX_COST_NUM, COL_RATING_NUM)
    corr_votes_rating = valid_df.stat.corr(COL_VOTES_NUM, COL_RATING_NUM)
    corr_cost_votes = valid_df.stat.corr(COL_APPROX_COST_NUM, COL_VOTES_NUM)

    return {
        "corr_cost_rating": round(corr_cost_rating, 4) if corr_cost_rating is not None else 0.0,
        "corr_votes_rating": round(corr_votes_rating, 4) if corr_votes_rating is not None else 0.0,
        "corr_cost_votes": round(corr_cost_votes, 4) if corr_cost_votes is not None else 0.0
    }


def analyze_high_engagement_restaurants(df: DataFrame, top_n: int = 15) -> DataFrame:
    """
    Identifies highest engagement establishments.
    Engagement Score is defined as (rating_num * log10(votes + 1)).
    """
    return (
        df.filter(F.col(COL_RATING_NUM).isNotNull() & (F.col(COL_VOTES_NUM) > 0))
        .withColumn(
            "engagement_score",
            F.round(F.col(COL_RATING_NUM) * F.log10(F.col(COL_VOTES_NUM) + 1), 2)
        )
        .select(
            COL_NAME, COL_LOCATION, COL_RATING_NUM, COL_VOTES_NUM,
            COL_APPROX_COST_NUM, COL_CUISINES, "engagement_score"
        )
        .orderBy(F.desc("engagement_score"))
        .limit(top_n)
    )


def compute_locality_cuisine_matrix(
    df: DataFrame,
    top_localities: int = 10,
    top_cuisines: int = 10
) -> DataFrame:
    """
    Constructs a two-dimensional matrix of top localities vs top cuisines.
    Computes restaurant density (count) for each combination for heatmap visualization.
    """
    # 1. Identify top N localities
    top_loc_list = [
        row[COL_LOCATION] for row in (
            df.filter(F.col(COL_LOCATION).isNotNull() & (F.col(COL_LOCATION) != ""))
            .groupBy(COL_LOCATION)
            .count()
            .orderBy(F.desc("count"))
            .limit(top_localities)
            .collect()
        )
    ]

    # 2. Identify top N cuisines
    top_cui_list = [
        row["cuisine_item"] for row in (
            df.filter(F.col(COL_CUISINES).isNotNull() & (F.col(COL_CUISINES) != ""))
            .withColumn("cuisine_item", F.explode(F.split(F.col(COL_CUISINES), r",\s*")))
            .filter(F.col("cuisine_item") != "")
            .groupBy("cuisine_item")
            .count()
            .orderBy(F.desc("count"))
            .limit(top_cuisines)
            .collect()
        )
    ]

    # 3. Filter DataFrame to these top items and explode
    matrix_df = (
        df.filter(F.col(COL_LOCATION).isin(top_loc_list))
        .withColumn("cuisine_item", F.explode(F.split(F.col(COL_CUISINES), r",\s*")))
        .filter(F.col("cuisine_item").isin(top_cui_list))
        .groupBy(COL_LOCATION)
        .pivot("cuisine_item", top_cui_list)
        .agg(F.count(COL_NAME))
        .na.fill(0)
    )

    return matrix_df
