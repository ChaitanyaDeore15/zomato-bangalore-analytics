# System Architecture & Technical Workflow

## 1. High-Level Project Architecture

The **Zomato Bangalore Restaurant Analytics** system is architected as an end-to-end Big Data Analytics solution decoupling high-throughput distributed processing (Apache Spark) from interactive visual exploration (Streamlit, Plotly, Seaborn).

```mermaid
flowchart TD
    subgraph Ingestion ["1. Data Ingestion Layer"]
        RAW["data/raw/zomato.csv<br/>(51,717 raw listings, 547 MB)"]
    end

    subgraph SparkCore ["2. Distributed Processing Engine (Apache Spark Core & SQL)"]
        SS["src/spark_session.py<br/>JVM 21 Modularity Flags"]
        LOADER["src/data_loader.py<br/>MultiLine CSV Reader"]
        CLEAN["src/data_cleaning.py<br/>Rating/Cost Parsing & Deduplication"]
        ANALYSIS["src/spark_analysis.py<br/>RDD Operations & Catalyst Aggregations"]
        SS --> LOADER
        RAW --> LOADER
        LOADER --> CLEAN
        CLEAN --> ANALYSIS
    end

    subgraph Storage ["3. Processed Data & Results Store"]
        CLEAN_CSV["data/processed/zomato_cleaned.csv<br/>(12,519 unique establishments)"]
        CSV_AGG["outputs/analysis_results/*.csv<br/>(Locality, Cuisines, Matrices, Audit)"]
        CLEAN --> CLEAN_CSV
        ANALYSIS --> CSV_AGG
    end

    subgraph Presentation ["4. Visual Analytics & Presentation Layer"]
        NB["notebooks/ 01 - 04<br/>Interactive Jupyter Labs"]
        CHARTS["visualizations/<br/>chart_generation.py<br/>heatmap_analysis.py<br/>geospatial_analysis.py"]
        DASH["dashboard/app.py<br/>Streamlit Interactive Portal"]
        OUT_CHARTS["outputs/charts/*.png<br/>outputs/interactive_charts/*.html"]
        
        CSV_AGG --> NB
        CLEAN_CSV --> NB
        CSV_AGG --> CHARTS
        CLEAN_CSV --> CHARTS
        CHARTS --> OUT_CHARTS
        CSV_AGG --> DASH
        CLEAN_CSV --> DASH
    end
```

---

## 2. Component Responsibility Breakdown

| Component | File Path | Primary Responsibilities | Dependencies |
| :--- | :--- | :--- | :--- |
| **Spark Engine** | `src/spark_session.py` | Configures JVM flags for Java 21 LTS, allocates local worker cores (`local[*]`), configures shuffle partitions (8), and exposes managed SparkSession factory. | `pyspark`, `Java 21` |
| **Data Ingestion** | `src/data_loader.py` | Ingests multi-line CSVs with embedded quote escapes. Provides schema inspection and row count telemetry. | `src/spark_session.py` |
| **Data Cleaning** | `src/data_cleaning.py` | Normalizes strings, parses `rate` (`'4.1/5'` to `4.1`; `'NEW'`/`'-'` to `null`), cleans `approx_cost` (strips `,`), and eliminates multi-zone listing duplicates on `[name, address, location]`. | `src/config.py` |
| **Spark Analytics** | `src/spark_analysis.py` | Executes RDD operations (`map`, `filter`, `flatMap`, `reduceByKey`) and Catalyst DataFrame aggregations. Computes locality profiles, thresholded cuisine ratings, price tiers, correlations, and 2D locality-cuisine matrices. | `src/config.py`, `pyspark.sql` |
| **Pipeline Runner** | `src/export_results.py` | Orchestrates the entire processing lifecycle and persists cleaned datasets and aggregated CSVs to `outputs/analysis_results/`. | `src/*` |
| **Static Visualizer** | `visualizations/chart_generation.py` | Generates 300 DPI Matplotlib/Seaborn figures for formal academic reports. | `matplotlib`, `seaborn`, `pandas` |
| **Heatmap Engine** | `visualizations/heatmap_analysis.py` | Constructs high-dimensional locality vs. cuisine supply matrix heatmaps in static PNG and interactive HTML formats. | `seaborn`, `plotly` |
| **Spatial Engine** | `visualizations/geospatial_analysis.py` | Analyzes geographic concentration percentiles (Pareto distribution) and spatial density clusters without inventing synthetic coordinates. | `matplotlib`, `plotly` |
| **Streamlit Portal**| `dashboard/app.py` | Interactive web dashboard featuring real-time sidebar filters, dynamic KPI metrics, and tabbed analytical views. | `streamlit`, `plotly` |

---

## 3. Detailed Data Flow Architecture

```mermaid
sequenceDiagram
    autonumber
    actor User as Analyst / Faculty
    participant Script as src/export_results.py
    participant Spark as Apache Spark Cluster
    participant Store as outputs/analysis_results/
    participant Vis as visualizations/
    participant Dash as dashboard/app.py

    User->>Script: Execute Pipeline
    Script->>Spark: Initialize SparkSession (JVM 21 options)
    Script->>Spark: Ingest data/raw/zomato.csv (51,717 rows)
    Spark->>Spark: Clean numeric ratings, strip commas, deduplicate entities
    Note over Spark: 12,519 Unique Establishments Cached
    Spark->>Spark: Run RDD flatMap + reduceByKey on cuisines
    Spark->>Spark: GroupBy Locality, Pivot Cuisines, Calculate Pearson Corrs
    Spark->>Store: Export aggregated summary tables (.csv & .json)
    Script-->>User: Pipeline Complete
    
    User->>Vis: Run chart generation scripts
    Store->>Vis: Ingest summary tables
    Vis->>Vis: Render PNG (300 DPI) & HTML (Plotly)
    Vis-->>User: Outputs saved to outputs/charts/
    
    User->>Dash: Launch Streamlit Web App
    Store->>Dash: Load lightweight cached aggregated metrics
    Dash-->>User: Interactive exploration with dynamic filtering
```

---

## 4. Optimization & Modularity Strategies

1. **Catalyst Optimizer Leverage**: All analytical aggregations are constructed using native DataFrame expressions before an action is invoked, enabling Catalyst projection pruning and predicate pushdown.
2. **Decoupled Browser Layer**: The Streamlit dashboard never loads or processes the heavy 547 MB raw dataset during user interactions. Instead, it operates exclusively on the pre-aggregated Spark summaries and the compact cleaned CSV, guaranteeing responsive sub-second UI interactions.
3. **Lazy Evaluation & Caching**: Cleaned DataFrames are persisted in Spark memory (`cache()`) prior to executing the 9 analytical queries, avoiding redundant disk re-reads.
