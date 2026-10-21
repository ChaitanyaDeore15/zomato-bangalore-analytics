"""
Project Configuration Module
Defines project paths, Spark settings, threshold constants, and column specifications.
"""

from pathlib import Path
import os
import sys

# Base project paths (resolved dynamically)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_DATASET_PATH = RAW_DATA_DIR / "zomato.csv"
CLEANED_DATASET_PARQUET = PROCESSED_DATA_DIR / "zomato_cleaned.parquet"
CLEANED_DATASET_CSV = PROCESSED_DATA_DIR / "zomato_cleaned.csv"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"
INTERACTIVE_CHARTS_DIR = OUTPUTS_DIR / "interactive_charts"
ANALYSIS_RESULTS_DIR = OUTPUTS_DIR / "analysis_results"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# Ensure all primary output directories exist
for d in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUTS_DIR, CHARTS_DIR,
          INTERACTIVE_CHARTS_DIR, ANALYSIS_RESULTS_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Spark Configuration
APP_NAME = "Zomato_Bangalore_Restaurant_Analytics"
SPARK_MASTER = os.environ.get("SPARK_MASTER", "local[*]")
SPARK_DRIVER_MEMORY = os.environ.get("SPARK_DRIVER_MEMORY", "4g")

# Analytical Thresholds
MIN_CUISINE_SAMPLE_SIZE = 30  # Minimum restaurants required for ranking a cuisine reliably
TOP_N_LOCALITIES = 10
TOP_N_CUISINES = 15

# Raw Column Names
COL_URL = "url"
COL_ADDRESS = "address"
COL_NAME = "name"
COL_ONLINE_ORDER = "online_order"
COL_BOOK_TABLE = "book_table"
COL_RATE = "rate"
COL_VOTES = "votes"
COL_PHONE = "phone"
COL_LOCATION = "location"
COL_REST_TYPE = "rest_type"
COL_DISH_LIKED = "dish_liked"
COL_CUISINES = "cuisines"
COL_APPROX_COST = "approx_cost(for two people)"
COL_REVIEWS_LIST = "reviews_list"
COL_MENU_ITEM = "menu_item"
COL_LISTED_IN_TYPE = "listed_in(type)"
COL_LISTED_IN_CITY = "listed_in(city)"

# Cleaned Column Names
COL_RATING_NUM = "rating_num"
COL_APPROX_COST_NUM = "approx_cost_num"
COL_VOTES_NUM = "votes_num"
COL_CUISINE_SINGLE = "cuisine_single"
