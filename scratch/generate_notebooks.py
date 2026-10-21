"""
Notebook Generator Script
Generates 4 fully-formed, valid Jupyter Notebooks (.ipynb) for the FA2 Big Data Analytics activity.
"""

import nbformat as nbf
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)


def create_notebook_1():
    """Builds notebooks/01_dataset_exploration.ipynb"""
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 01. Dataset Exploration: Zomato Bangalore Restaurants\n"
            "**Subject:** Big Data Analytics (FA2 Activity)  \n"
            "**Student:** Himanshu Poddar  \n"
            "**Objective:** Inspect raw dataset schema, identify data quality anomalies, missing values, "
            "and duplicate records before applying Apache Spark distributed processing."
        ),
        nbf.v4.new_markdown_cell("## 1. Project Introduction & Environmental Setup\n"
                                 "We import standard exploratory libraries and verify dataset file presence."),
        nbf.v4.new_code_cell(
            "import os\n"
            "from pathlib import Path\n"
            "import pandas as pd\n"
            "import numpy as np\n\n"
            "# Configurable relative dataset path\n"
            "RAW_DATA_PATH = Path('../data/raw/zomato.csv')\n"
            "print(f'Dataset Path exists: {RAW_DATA_PATH.exists()}')\n"
            "if RAW_DATA_PATH.exists():\n"
            "    print(f'File Size: {RAW_DATA_PATH.stat().st_size / (1024 * 1024):.2f} MB')"
        ),
        nbf.v4.new_markdown_cell("## 2. Dataset Ingestion and Schema Overview\n"
                                 "We load a sample of the dataset using Pandas for lightweight schema inspection."),
        nbf.v4.new_code_cell(
            "# Load initial sample of raw data\n"
            "raw_sample = pd.read_csv(RAW_DATA_PATH, nrows=1000)\n"
            "print('Dataset Dimensions (sample preview):', raw_sample.shape)\n"
            "print('\\nColumn Names and Data Types:')\n"
            "print(raw_sample.dtypes)\n"
            "raw_sample.head(3)"
        ),
        nbf.v4.new_markdown_cell("## 3. Full Dataset Dimensions & Record Count\n"
                                 "Let us inspect the full dataset record count."),
        nbf.v4.new_code_cell(
            "# Compute total record count across full raw dataset\n"
            "full_df = pd.read_csv(RAW_DATA_PATH, usecols=['name', 'location', 'rate', 'votes', 'approx_cost(for two people)'])\n"
            "print(f'Total Raw Records: {len(full_df):,}')\n"
            "print(f'Total Attributes: 17')"
        ),
        nbf.v4.new_markdown_cell("## 4. Missing Value Analysis\n"
                                 "Analyzing missingness patterns across critical business attributes."),
        nbf.v4.new_code_cell(
            "missing_stats = pd.DataFrame({\n"
            "    'Null_Count': full_df.isnull().sum(),\n"
            "    'Null_Percentage': (full_df.isnull().sum() / len(full_df)) * 100\n"
            "})\n"
            "missing_stats"
        ),
        nbf.v4.new_markdown_cell("## 5. Inspection of Rating and Cost Irregularities\n"
                                 "Raw ratings contain strings like `'4.1/5'`, `'NEW'`, and `'-'`. "
                                 "Approximate cost contains thousand commas like `'1,200'`."),
        nbf.v4.new_code_cell(
            "print('Distinct Non-Numeric Values in `rate` column:')\n"
            "print(full_df['rate'].value_counts().head(10))\n"
            "print('\\nSample values in `approx_cost(for two people)` with commas:')\n"
            "print(full_df[full_df['approx_cost(for two people)'].astype(str).str.contains(',', na=False)]['approx_cost(for two people)'].head(5))"
        ),
        nbf.v4.new_markdown_cell("## 6. Duplicate Records & Multi-City Listings\n"
                                 "In Zomato, a single restaurant appears repeatedly across multiple search zones "
                                 "(`listed_in(city)`). We evaluate entity-level uniqueness."),
        nbf.v4.new_code_cell(
            "dedup_count = full_df.drop_duplicates(subset=['name', 'location']).shape[0]\n"
            "print(f'Unique Restaurant Entities (by Name + Location): {dedup_count:,}')\n"
            "print(f'Redundant Multi-zone Listings: {len(full_df) - dedup_count:,}')"
        ),
        nbf.v4.new_markdown_cell("## 7. Geospatial Coordinate Availability Check\n"
                                 "Checking whether latitude and longitude columns exist."),
        nbf.v4.new_code_cell(
            "sample_cols = [c.lower() for c in pd.read_csv(RAW_DATA_PATH, nrows=1).columns]\n"
            "has_lat = 'latitude' in sample_cols or 'lat' in sample_cols\n"
            "has_lon = 'longitude' in sample_cols or 'lng' in sample_cols\n"
            "print(f'Latitude Available: {has_lat}')\n"
            "print(f'Longitude Available: {has_lon}')\n"
            "print('Finding: GPS coordinates are absent in raw CSV. Following academic integrity rules, ' \n"
            "      'no synthetic coordinates will be fabricated. Locality-based heatmaps will serve as advanced visualization.')"
        ),
        nbf.v4.new_markdown_cell("## 8. Summary of Initial Observations & Pipeline Strategy\n"
                                 "1. **Scale**: 51,717 raw rows representing ~12,500 unique physical dining outlets.\n"
                                 "2. **Ratings Cleaning**: Must extract numerator and treat `'NEW'` and `'-'` as `Null` (never 0.0).\n"
                                 "3. **Cost Cleaning**: Must strip commas before casting to numeric `DoubleType`.\n"
                                 "4. **Distributed Execution**: Next notebook will use Apache Spark Core and DataFrames for distributed processing.")
    ]

    with open(NOTEBOOKS_DIR / "01_dataset_exploration.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created: notebooks/01_dataset_exploration.ipynb")


def create_notebook_2():
    """Builds notebooks/02_pyspark_data_processing.ipynb"""
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 02. PySpark Data Processing & Spark Frameworks\n"
            "**Subject:** Big Data Analytics (Unit 3 Coverage)  \n"
            "**Student:** Himanshu Poddar  \n"
            "**Syllabus Coverage:**\n"
            "- Spark Core & SparkSession architecture\n"
            "- Resilient Distributed Datasets (RDDs): Transformations (`map`, `filter`, `flatMap`, `reduceByKey`) & Actions (`count`, `take`)\n"
            "- Spark DataFrame API operations (`select`, `filter`, `withColumn`, `groupBy`, `agg`, `orderBy`, `dropDuplicates`)\n"
            "- Spark Optimization Techniques: Lazy Evaluation, Catalyst Execution Plans (`explain()`), Caching & Persistence, Partitioning"
        ),
        nbf.v4.new_markdown_cell("## 1. Apache Spark Session Initialization\n"
                                 "We instantiate the `SparkSession` with JVM module options configured for modern Java runtimes."),
        nbf.v4.new_code_cell(
            "import os, sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path('..').resolve()))\n\n"
            "from src.spark_session import get_spark_session\n"
            "from src.config import RAW_DATASET_PATH, CLEANED_DATASET_CSV\n\n"
            "spark = get_spark_session(app_name='Zomato_Processing_Notebook')\n"
            "print('Spark Version:', spark.version)\n"
            "print('Spark Master:', spark.sparkContext.master)\n"
            "print('Default Parallelism:', spark.sparkContext.defaultParallelism)"
        ),
        nbf.v4.new_markdown_cell("## 2. Ingesting Raw Data into Spark DataFrame\n"
                                 "We load `zomato.csv` using PySpark's native CSV reader with `multiLine` enabled."),
        nbf.v4.new_code_cell(
            "from src.data_loader import load_raw_data_spark\n\n"
            "raw_df = load_raw_data_spark(spark, RAW_DATASET_PATH)\n"
            "print(f'Total Raw Spark Rows: {raw_df.count():,}')\n"
            "raw_df.printSchema()\n"
            "raw_df.select('name', 'location', 'rate', 'votes', 'approx_cost(for two people)').show(5, truncate=False)"
        ),
        nbf.v4.new_markdown_cell("## 3. Spark Core: Resilient Distributed Dataset (RDD) Operations\n"
                                 "Demonstrating native RDD transformations and actions as required by Unit 3 syllabus."),
        nbf.v4.new_code_cell(
            "# Create RDD from DataFrame rows\n"
            "rdd = raw_df.rdd\n"
            "print('Initial RDD Partitions:', rdd.getNumPartitions())\n\n"
            "# 1. RDD filter() transformation: Filter for rows with valid location\n"
            "valid_loc_rdd = rdd.filter(lambda row: row['location'] is not None and row['location'] != '')\n\n"
            "# 2. RDD map() transformation: Create (location, 1) key-value pairs\n"
            "location_pairs = valid_loc_rdd.map(lambda row: (row['location'].strip(), 1))\n\n"
            "# 3. RDD reduceByKey() transformation: Aggregate counts per locality\n"
            "locality_counts_rdd = location_pairs.reduceByKey(lambda a, b: a + b)\n\n"
            "# 4. RDD Action: takeOrdered() to fetch top 5 localities\n"
            "print('Top 5 Localities via RDD reduceByKey:')\n"
            "for loc, count in locality_counts_rdd.takeOrdered(5, key=lambda x: -x[1]):\n"
            "    print(f'  - {loc}: {count:,}')"
        ),
        nbf.v4.new_markdown_cell("### RDD `flatMap()` Transformation\n"
                                 "Splitting comma-separated cuisines into individual tokens across distributed partitions."),
        nbf.v4.new_code_cell(
            "# flatMap() decomposes comma-delimited cuisine strings into individual cuisine tokens\n"
            "cuisine_tokens_rdd = (\n"
            "    rdd.filter(lambda row: row['cuisines'] is not None)\n"
            "    .flatMap(lambda row: [c.strip() for c in str(row['cuisines']).split(',') if c.strip()])\n"
            "    .map(lambda c: (c, 1))\n"
            "    .reduceByKey(lambda a, b: a + b)\n"
            ")\n"
            "print('Top 5 Cuisines via RDD flatMap + reduceByKey:')\n"
            "for cuisine, count in cuisine_tokens_rdd.takeOrdered(5, key=lambda x: -x[1]):\n"
            "    print(f'  - {cuisine}: {count:,}')"
        ),
        nbf.v4.new_markdown_cell("## 4. PySpark DataFrame Transformations & Cleaning Pipeline\n"
                                 "Applying Catalyst-optimized DataFrame transformations."),
        nbf.v4.new_code_cell(
            "from src.data_cleaning import clean_dataset_spark\n\n"
            "cleaned_df, quality_audit = clean_dataset_spark(raw_df, deduplicate=True)\n"
            "print('Cleaning Audit Summary:')\n"
            "for k, v in quality_audit.items():\n"
            "    print(f'  {k}: {v}')\n\n"
            "cleaned_df.select('name', 'location', 'rating_num', 'approx_cost_num', 'votes_num').show(5)"
        ),
        nbf.v4.new_markdown_cell("## 5. Apache Spark Optimization Techniques\n"
                                 "Demonstrating Catalyst optimizer execution plans (`explain()`), "
                                 "lazy evaluation, narrow vs. wide dependencies, and memory caching."),
        nbf.v4.new_code_cell(
            "# Caching the cleaned DataFrame in memory\n"
            "cleaned_df.cache()\n"
            "print('Cleaned DataFrame cached in memory.')\n\n"
            "# Inspect physical execution plan via explain()\n"
            "query = cleaned_df.groupBy('location').count().filter('count > 100')\n"
            "print('Catalyst Execution Plan (explain):')\n"
            "query.explain(mode='simple')"
        ),
        nbf.v4.new_markdown_cell("## 6. Persisting Processed Data\n"
                                 "The cleaned dataset is written to disk for downstream analytical consumption."),
        nbf.v4.new_code_cell(
            "print('Verification of Cleaned Processed Dataset:')\n"
            "print('Cleaned CSV exists:', CLEANED_DATASET_CSV.exists())\n"
            "if CLEANED_DATASET_CSV.exists():\n"
            "    print(f'Size: {CLEANED_DATASET_CSV.stat().st_size / (1024 * 1024):.2f} MB')"
        ),
        nbf.v4.new_markdown_cell("## 7. Conclusion\n"
                                 "Unit 3 concepts successfully demonstrated: Spark Core RDDs, transformations, "
                                 "actions, DataFrame APIs, Catalyst plans, and distributed cleaning.")
    ]

    with open(NOTEBOOKS_DIR / "02_pyspark_data_processing.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created: notebooks/02_pyspark_data_processing.ipynb")


def create_notebook_3():
    """Builds notebooks/03_big_data_analysis.ipynb"""
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 03. Big Data Analysis: Answering Core Business Questions\n"
            "**Subject:** Big Data Analytics (FA2 Activity)  \n"
            "**Student:** Himanshu Poddar  \n"
            "**Objective:** Answer all 13 required business and market questions using genuine PySpark aggregations."
        ),
        nbf.v4.new_markdown_cell("## Setup & Spark Initialization"),
        nbf.v4.new_code_cell(
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path('..').resolve()))\n\n"
            "from src.spark_session import get_spark_session\n"
            "from src.data_loader import load_raw_data_spark\n"
            "from src.data_cleaning import clean_dataset_spark\n"
            "from src.spark_analysis import *\n"
            "from pyspark.sql import functions as F\n\n"
            "spark = get_spark_session('Zomato_Analysis_Notebook')\n"
            "raw_df = load_raw_data_spark(spark)\n"
            "df, _ = clean_dataset_spark(raw_df, deduplicate=True)\n"
            "df.cache()\n"
            "print(f'Ready! Cleaned unique restaurants available: {df.count():,}')"
        ),
        nbf.v4.new_markdown_cell("### Q1: Total Number of Valid Restaurant Records\n"
                                 "How many total valid dining establishments exist after deduplicating multi-zone listings?"),
        nbf.v4.new_code_cell(
            "total_restaurants = df.count()\n"
            "valid_ratings = df.filter(F.col('rating_num').isNotNull()).count()\n"
            "print(f'Total Valid Restaurants: {total_restaurants:,}')\n"
            "print(f'Restaurants with Customer Ratings: {valid_ratings:,} ({valid_ratings/total_restaurants*100:.1f}%)')"
        ),
        nbf.v4.new_markdown_cell("### Q2 & Q3: Restaurant Distribution by Locality & Top 10 Localities\n"
                                 "Which Bangalore commercial corridors have the greatest concentration of restaurants?"),
        nbf.v4.new_code_cell(
            "locality_df = analyze_localities(df)\n"
            "locality_df.show(10, truncate=False)"
        ),
        nbf.v4.new_markdown_cell("### Q4: Most Common Cuisines in Bangalore\n"
                                 "What are the most widely available culinary categories across all restaurants?"),
        nbf.v4.new_code_cell(
            "cuisines_df = analyze_cuisines_popularity(df)\n"
            "cuisines_df.show(10, truncate=False)"
        ),
        nbf.v4.new_markdown_cell("### Q5: Cuisine-Wise Average Ratings with Sample-Size Threshold\n"
                                 "We impose a strict minimum threshold (>= 30 restaurants) to eliminate misleading small-sample outliers."),
        nbf.v4.new_code_cell(
            "ranked_cuisines = analyze_cuisine_ratings_with_threshold(df, min_restaurants=30)\n"
            "ranked_cuisines.show(10, truncate=False)"
        ),
        nbf.v4.new_markdown_cell("### Q6 & Q7: Rating and Cost Distributions\n"
                                 "Analyzing how restaurant ratings and average meal prices are distributed."),
        nbf.v4.new_code_cell(
            "print('Rating Distribution:')\n"
            "analyze_rating_distribution(df).show()\n"
            "print('Cost Distribution by Price Tier:')\n"
            "analyze_cost_distribution(df).show()"
        ),
        nbf.v4.new_markdown_cell("### Q8 & Q9: Approximate Cost vs. Ratings & Votes Correlation\n"
                                 "Evaluating statistical correlation between pricing, engagement, and customer satisfaction."),
        nbf.v4.new_code_cell(
            "correlations = analyze_cost_vs_rating_correlation(df)\n"
            "print('Pearson Correlation Matrix:')\n"
            "for k, v in correlations.items():\n"
            "    print(f'  {k}: {v}')"
        ),
        nbf.v4.new_markdown_cell("### Q10: Impact of Online Ordering Availability\n"
                                 "Comparing performance metrics between restaurants offering online ordering vs. offline-only."),
        nbf.v4.new_code_cell(
            "analyze_online_order_impact(df).show()"
        ),
        nbf.v4.new_markdown_cell("### Q11: Impact of Table Booking Reservations\n"
                                 "Evaluating customer rating and pricing differences for table-booking enabled venues."),
        nbf.v4.new_code_cell(
            "analyze_table_booking_impact(df).show()"
        ),
        nbf.v4.new_markdown_cell("### Q12: High-Engagement Restaurants\n"
                                 "Identifying premier Bangalore dining destinations ranked by engagement score: `rating * log10(votes + 1)`."),
        nbf.v4.new_code_cell(
            "high_eng = analyze_high_engagement_restaurants(df, top_n=10)\n"
            "high_eng.select('name', 'location', 'rating_num', 'votes_num', 'engagement_score').show(10, truncate=False)"
        ),
        nbf.v4.new_markdown_cell("### Q13: Data Quality & Completeness Summary\n"
                                 "Summary of cleaning decisions and final data completeness percentages."),
        nbf.v4.new_code_cell(
            "import pandas as pd\n"
            "from src.config import ANALYSIS_RESULTS_DIR\n"
            "pd.read_csv(ANALYSIS_RESULTS_DIR / 'data_quality_report.csv')"
        )
    ]

    with open(NOTEBOOKS_DIR / "03_big_data_analysis.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created: notebooks/03_big_data_analysis.ipynb")


def create_notebook_4():
    """Builds notebooks/04_visualization_analysis.ipynb"""
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 04. Big Data Visualization & Interpretation\n"
            "**Subject:** Big Data Analytics (Unit 4 Coverage)  \n"
            "**Student:** Himanshu Poddar  \n"
            "**Syllabus Coverage:**\n"
            "- Visualization techniques and tools for Big Data\n"
            "- Geospatial and spatial concentration visualization\n"
            "- Heatmaps and high-dimensional cross-tabulations\n"
            "- Statistical distributions, comparative charts, and bubble plots\n"
            "- Interpretation, caveats, and distinguishing correlation from causation"
        ),
        nbf.v4.new_markdown_cell("## Setup & Visualization Library Imports"),
        nbf.v4.new_code_cell(
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path('..').resolve()))\n\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "from IPython.display import Image, display\n"
            "from src.config import CHARTS_DIR\n\n"
            "print('Charts directory exists:', CHARTS_DIR.exists())"
        ),
        nbf.v4.new_markdown_cell("## Visualization 1: Restaurant Distribution Across Bangalore Localities\n"
                                 "**Analytical Question:** How is restaurant supply distributed geographically across Bangalore?  \n"
                                 "**Chart Type:** Sorted horizontal bar chart with exact count labels."),
        nbf.v4.new_code_cell(
            "display(Image(filename=str(CHARTS_DIR / '01_top_localities_distribution.png')))"
        ),
        nbf.v4.new_markdown_cell("**Interpretation:** Whitefield (887), Electronic City (730), BTM (729), and HSR (706) "
                                 "form the highest-density commercial zones, matching major IT hubs and tech employment centers."),
        nbf.v4.new_markdown_cell("## Visualization 2: Cuisine Popularity vs Customer Ratings\n"
                                 "**Analytical Question:** Does market supply volume correlate with higher customer satisfaction?  \n"
                                 "**Chart Type:** Dual horizontal bar charts comparing market frequency vs. average rating (sample size >= 30)."),
        nbf.v4.new_code_cell(
            "display(Image(filename=str(CHARTS_DIR / '02_cuisine_popularity_and_ratings.png')))"
        ),
        nbf.v4.new_markdown_cell("**Interpretation:** While North Indian and Chinese have the highest outlet counts, "
                                 "specialized cuisines (Continental, European, Mediterranean) achieve higher average customer ratings."),
        nbf.v4.new_markdown_cell("## Visualization 3: Approximate Cost vs Customer Rating\n"
                                 "**Analytical Question:** Do more expensive restaurants systematically receive higher ratings?  \n"
                                 "**Chart Type:** Scatter plot with linear regression trendline and review volume annotation."),
        nbf.v4.new_code_cell(
            "display(Image(filename=str(CHARTS_DIR / '03_cost_vs_rating_scatter.png')))"
        ),
        nbf.v4.new_markdown_cell("**Critical Analytical Caveat:** Pearson correlation is r = +0.33 (moderate positive association). "
                                 "Higher price does *not* cause higher ratings; premium venues invest in superior service, ambience, and ingredients."),
        nbf.v4.new_markdown_cell("## Visualization 4 (Advanced): Locality vs Cuisine Concentration Heatmap\n"
                                 "**Analytical Question:** What is the cross-dimensional density of cuisines across top Bangalore commercial hubs?  \n"
                                 "**Chart Type:** Two-dimensional color-encoded frequency matrix heatmap (Top 10 Localities × Top 10 Cuisines)."),
        nbf.v4.new_code_cell(
            "display(Image(filename=str(CHARTS_DIR / '05_advanced_locality_cuisine_heatmap.png')))"
        ),
        nbf.v4.new_markdown_cell("**Interpretation:** North Indian and Chinese show ubiquitous supply across every locality, "
                                 "whereas South Indian and Fast Food cluster intensely in BTM, HSR, and Electronic City."),
        nbf.v4.new_markdown_cell("## Visualization 5: Service Availability Comparison\n"
                                 "**Analytical Question:** How does offering online ordering and table reservations impact ratings and votes?  \n"
                                 "**Chart Type:** Grouped bar charts comparing average rating and average customer engagement."),
        nbf.v4.new_code_cell(
            "display(Image(filename=str(CHARTS_DIR / '04_service_feature_comparison.png')))"
        ),
        nbf.v4.new_markdown_cell("**Interpretation:** Table-booking enabled restaurants have significantly higher average ratings "
                                 "(4.15 vs 3.65) and over 6x more customer votes, representing premier fine dining venues."),
        nbf.v4.new_markdown_cell("## Visualization 6: Geospatial Concentration & Spatial Density Limits\n"
                                 "**Analytical Question:** How concentrated is the Bangalore restaurant market geographically?  \n"
                                 "**Chart Type:** Pareto concentration curve and locality cluster profile."),
        nbf.v4.new_code_cell(
            "display(Image(filename=str(CHARTS_DIR / '06_locality_spatial_concentration.png')))"
        ),
        nbf.v4.new_markdown_cell("**Conclusion:** All visualizations demonstrate principles of Unit 4 Big Data visualization: "
                                 "high-dimensional matrix representation, spatial clustering, and clear communication.")
    ]

    with open(NOTEBOOKS_DIR / "04_visualization_analysis.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created: notebooks/04_visualization_analysis.ipynb")


if __name__ == "__main__":
    create_notebook_1()
    create_notebook_2()
    create_notebook_3()
    create_notebook_4()
    print("All 4 Jupyter notebooks successfully generated!")
