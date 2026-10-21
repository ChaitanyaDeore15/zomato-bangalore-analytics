# Zomato Bangalore Restaurant Analytics Using Apache Spark and Advanced Big Data Visualization

![Spark Analytics](outputs/charts/01_top_localities_distribution.png)

**Dataset:** Zomato Bangalore Restaurants Dataset (~547 MB, 51,717 raw listings)  
**Key Frameworks & Competencies:**
- **Distributed Computing with Apache Spark** (Spark Core, RDDs, transformations, actions, DataFrame operations, Catalyst optimizer, caching, partitioning)
- **Advanced Big Data Visualization** (Heatmaps, spatial concentration, scatter plots, distributions, comparative charts, interactive dashboards)

---

## 📋 Technical Implementation & Competencies Matrix

| Competency Area | Description | Implementation Evidence & File Locations |
| :--- | :--- | :--- |
| **Problem identification & understanding** | Real dataset inspection, missing values, duplicate structure, and data quality constraints identified. | Detailed in [REPORT.md](REPORT.md), [data_dictionary.md](data/data_dictionary.md), and [01_dataset_exploration.ipynb](notebooks/01_dataset_exploration.ipynb). |
| **Apache Spark implementation** | Real PySpark application featuring Spark Core RDDs (`map`, `filter`, `flatMap`, `reduceByKey`), DataFrame operations, lazy evaluation, in-memory caching (`cache()`), Catalyst execution plans (`explain()`), and partition tuning. | Implemented in [src/spark_session.py](src/spark_session.py), [src/data_cleaning.py](src/data_cleaning.py), and [src/spark_analysis.py](src/spark_analysis.py). |
| **Data analysis & results** | Calculated metrics across all 13 analytical questions with strict sample-size thresholds ($\ge 30$). | Output CSVs in [outputs/analysis_results/](outputs/analysis_results/) and code in [03_big_data_analysis.ipynb](notebooks/03_big_data_analysis.ipynb). |
| **Visualization techniques** | 6 high-resolution static charts (300 DPI) and 5 interactive HTML charts featuring advanced Locality $\times$ Cuisine Heatmap, Pareto spatial concentration curve, and bubble plots. | Rendered in [outputs/charts/](outputs/charts/), [outputs/interactive_charts/](outputs/interactive_charts/), and [04_visualization_analysis.ipynb](notebooks/04_visualization_analysis.ipynb). |
| **Insights & strategic interpretation** | Actionable recommendations, statistical correlation analysis ($r = +0.33$), and clear distinction between correlation and causation. | Detailed in [REPORT.md](REPORT.md) and [VIVA.md](VIVA.md). |

---

## 🗂️ Project Directory Structure

```text
zomato-bangalore-analytics/
|
|-- data/
|   |-- raw/
|   |   |-- .gitkeep
|   |   |-- zomato.csv                 <- Raw dataset (51,717 rows, 547 MB)
|   |-- processed/
|   |   |-- zomato_cleaned.csv         <- Cleaned unique restaurants (12,519 rows)
|   |-- README.md                      <- Dataset placement instructions
|   |-- data_dictionary.md             <- Complete column metadata & data types
|
|-- notebooks/
|   |-- 01_dataset_exploration.ipynb   <- Data profiling & quality inspection
|   |-- 02_pyspark_data_processing.ipynb <- Spark Core, RDDs, Catalyst execution plans
|   |-- 03_big_data_analysis.ipynb     <- 13 core business analytical questions
|   |-- 04_visualization_analysis.ipynb <- Visualization interpretation & caveats
|
|-- src/
|   |-- __init__.py
|   |-- config.py                      <- Project paths, thresholds, and constants
|   |-- spark_session.py               <- SparkSession factory with Java 21 LTS JVM flags
|   |-- data_loader.py                 <- Multi-line CSV PySpark reader
|   |-- data_cleaning.py               <- Rating/cost parsing and entity deduplication
|   |-- spark_analysis.py              <- RDD transformations & Catalyst aggregations
|   |-- export_results.py              <- End-to-end Spark pipeline runner
|
|-- visualizations/
|   |-- __init__.py
|   |-- chart_generation.py            <- Bar charts, scatter plots, dual comparisons
|   |-- geospatial_analysis.py         <- Spatial concentration & Pareto analysis
|   |-- heatmap_analysis.py            <- Advanced Locality x Cuisine 2D Heatmap
|
|-- dashboard/
|   |-- app.py                         <- Production Streamlit analytics dashboard
|   |-- components.py                  <- Reusable UI components and chart cards
|
|-- outputs/
|   |-- charts/                        <- 6 high-resolution 300 DPI static charts (.png)
|   |-- interactive_charts/            <- 5 interactive Plotly visualizations (.html)
|   |-- analysis_results/              <- Aggregated Spark analytical CSV result tables
|   |-- reports/                       <- Generated quality reports and metrics
|   |-- .gitkeep
|
|-- tests/
|   |-- test_data_cleaning.py          <- Unit tests for parsing and null handling
|   |-- test_spark_analysis.py         <- Tests for aggregations and threshold filters
|   |-- test_visualizations.py         <- Tests for chart integrity and file outputs
|
|-- requirements.txt                   <- Reproducible Python dependencies
|-- README.md                          <- This document
|-- REPORT.md                          <- Comprehensive analytical report
|-- VIVA.md                            <- Comprehensive technical viva preparation (20 Q&As)
|-- ARCHITECTURE.md                    <- System architecture & Mermaid flowcharts
|-- .gitignore
```

---

## 🛠️ Technology Stack & Requirements

- **Operating System:** Windows 10/11 (or Linux/macOS)
- **Python:** Python 3.10 (Recommended for PySpark 3.5 / 4.x compatibility)
- **Java Runtime:** Java 21 LTS (or Java 17/11) with `JAVA_HOME` configured
- **Distributed Engine:** Apache Spark / PySpark
- **Visual Analytics:** Matplotlib, Seaborn, Plotly
- **Interactive UI:** Streamlit
- **Testing Framework:** PyTest

---

## 🚀 Step-by-Step Setup & Execution Guide (Windows PowerShell)

### Step 1: Environment Setup
Open Windows PowerShell in the project root directory:

```powershell
# Verify Python 3.10 and Java availability
py -3.10 --version
java -version

# Set JAVA_HOME environment variable for the session
$env:JAVA_HOME = "C:\Program Files\Java\jdk-21"

# Install required packages
py -3.10 -m pip install -r requirements.txt
```

### Step 2: Dataset Verification
Ensure the raw `zomato.csv` is located at `data/raw/zomato.csv`.  
*(If missing, copy the 547 MB file into `data/raw/`)*:
```powershell
Test-Path "data/raw/zomato.csv"  # Should return True
```

### Step 3: Run the Apache Spark Processing Pipeline
Execute the complete Spark cleaning and analytical aggregation pipeline:
```powershell
py -3.10 src/export_results.py
```
*Expected Output:*
- Cleans and deduplicates 51,717 rows down to 12,519 unique establishments.
- Executes RDD `map`, `filter`, `flatMap`, and `reduceByKey` operations.
- Persists `data/processed/zomato_cleaned.csv` and 10 analytical CSVs in `outputs/analysis_results/`.

### Step 4: Generate All Visualizations
Generate all 300 DPI static figures and interactive HTML charts:
```powershell
py -3.10 visualizations/chart_generation.py
py -3.10 visualizations/heatmap_analysis.py
py -3.10 visualizations/geospatial_analysis.py
```
*Outputs generated in `outputs/charts/` and `outputs/interactive_charts/`.*

### Step 5: Launch the Streamlit Interactive Dashboard
Run the analytics dashboard in your browser:
```powershell
py -3.10 -m streamlit run dashboard/app.py
```
*The interactive dashboard will automatically open at `http://localhost:8501`.*

### Step 6: Run Automated Tests
Execute the automated test suite verifying data cleaning, Spark queries, and chart files:
```powershell
py -3.10 -m pytest tests/
```
*Result: 11 passed in ~3 minutes (100% pass rate).*

---

## 📊 Summary of Analytical Findings

1. **Spatial Hubs**: Whitefield (887), Electronic City (730), BTM (729), and HSR (706) form Bangalore's largest restaurant clusters.
2. **Cuisine Saturation**: North Indian (5,050 outlets) and Chinese (3,600 outlets) represent the most saturated market segments.
3. **Cuisine Quality vs Volume**: High-volume cuisines suffer from quality variation, while specialty cuisines (Continental: 3.89, European: 3.87) achieve significantly higher customer satisfaction.
4. **Table Booking Impact**: Outlets offering table booking average a **4.15 / 5.0** rating with over **6x higher review volume** compared to non-booking venues (3.65 / 5.0).
5. **Price-to-Rating Association**: Pearson correlation between meal cost and rating is **$r = +0.33$**. Higher price reflects greater capital investment in quality ingredients and ambiance, but does not directly cause high ratings.

---

## 🔧 Troubleshooting Guide

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `FileNotFoundException: HADOOP_HOME and hadoop.home.dir are unset` | Spark default warning on Windows when Hadoop native binaries (`winutils.exe`) are not configured. | Safe to ignore for local Spark execution; all built-in Java/POSIX file systems function correctly. |
| `Cannot run program "python3"` in PySpark worker | Windows uses `python.exe` instead of POSIX `python3`. | Handled automatically in `src/spark_session.py` by setting `PYSPARK_PYTHON = sys.executable`. |
| `IllegalAccessError` under Java 17/21 | Strong encapsulation introduced in modern JVMs prevents reflective access to internal packages. | Resolved in `src/spark_session.py` using `--add-opens=java.base/java.lang=ALL-UNNAMED` and related JVM flags. |

---

## 📚 References & Syllabus Mapping

- **Unit 3: Apache Spark Frameworks**: Demonstrated in [02_pyspark_data_processing.ipynb](notebooks/02_pyspark_data_processing.ipynb), [src/spark_session.py](src/spark_session.py), [src/spark_analysis.py](src/spark_analysis.py).
- **Unit 4: Visualization Techniques for Big Data**: Demonstrated in [04_visualization_analysis.ipynb](notebooks/04_visualization_analysis.ipynb), [visualizations/](visualizations/), [outputs/charts/](outputs/charts/).
- **Formal Academic Report**: Complete documentation formatted for university evaluation in [REPORT.md](REPORT.md).
- **Faculty Viva Preparation**: 20 comprehensive technical questions and answers in [VIVA.md](VIVA.md).
