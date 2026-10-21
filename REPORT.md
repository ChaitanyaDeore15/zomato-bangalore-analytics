# Zomato Bangalore Restaurant Analytics Using Apache Spark and Advanced Big Data Visualization

---

**Academic Project Report**  
**Course:** Big Data Analytics  
**Activity:** FA2 Problem-Based Solving Activity  
**Student Name:** Himanshu Poddar  
**Dataset:** Zomato Bangalore Restaurants Dataset (Kaggle / College Repository)  
**Core Technologies:** Apache Spark (PySpark), Python 3.10, Matplotlib, Seaborn, Plotly, Streamlit, PyTest  
**Syllabus Focus:** Unit 3 (Apache Spark Frameworks) & Unit 4 (Visualization Techniques for Big Data)  
**Date of Submission:** October 2026  

---

## 1. Abstract

The exponential growth of urban dining ecosystems has created high-volume consumer transaction datasets that exceed traditional single-node analytical capabilities. This report presents an academic and practical implementation of Big Data analytics applied to the **Zomato Bangalore Restaurants** dataset (51,717 raw listings, ~547 MB). Using **Apache Spark (PySpark)** as the distributed computing backbone, we implement Resilient Distributed Datasets (RDDs), Catalyst-optimized DataFrame transformations, and memory caching to clean, normalize, and analyze the market. 

Entity-level deduplication resolved multi-zone listings down to 12,519 unique establishments. Exploratory and bivariate queries revealed that Whitefield, Electronic City, and BTM are Bangalore's densest culinary corridors, while North Indian and Chinese account for the highest market supply. High-dimensional cross-tabulations and an advanced Locality-versus-Cuisine heatmap demonstrate clear spatial preferences. Bivariate analysis established a moderate positive correlation between cost and customer ratings ($r = +0.33$), while table-booking venues achieved significantly higher engagement (4.15 average rating vs. 3.65 for non-booking). An interactive Streamlit dashboard and comprehensive automated test suite validate the reproducibility and academic rigor of the solution.

---

## 2. Introduction & Background

Bangalore, widely recognized as the technology capital of India, features one of the most culturally diverse and commercially dense food service markets in Asia. Online aggregators like Zomato act as digital intermediaries connecting millions of diners with tens of thousands of culinary vendors.

Analyzing this ecosystem requires handling unstructured text, missing ratings, multi-category tags, and skewed customer review distributions. In standard data engineering practice, performing iterative exploratory analytics on such multi-gigabyte datasets using single-threaded tools like standard Pandas results in high memory footprints, long computation latencies, and frequent Out-Of-Memory (OOM) failures. This project demonstrates how **Apache Spark** resolves these bottlenecks by distributing computation across partitions and coordinating transformations through lazy evaluation and Catalyst query optimization.

---

## 3. Problem Identification & Problem Statement

### 3.1 Problem Identification
Restaurant entrepreneurs, investors, and consumers face significant information asymmetry:
1. **Commercial Location Overcrowding**: New restaurateurs often establish outlets in heavily saturated zones without understanding localized cuisine deficits.
2. **Pricing and Quality Confusion**: Diners often assume higher meal pricing directly guarantees superior culinary quality.
3. **Delivery vs. Dine-in Dynamics**: Food businesses struggle to quantify the actual rating and engagement advantages of enabling digital table reservations and online delivery.

### 3.2 Formal Problem Statement
To engineer a scalable Big Data pipeline using Apache Spark Core and DataFrames alongside advanced statistical visualization techniques to ingest, sanitize, and analyze the Zomato Bangalore restaurant ecosystem, identifying market concentration, cuisine popularity, price-rating relationships, and data quality dynamics without fabricating unverified spatial coordinates.

---

## 4. Objectives of the Study

1. **Distributed Ingestion & Preprocessing**: Implement a robust PySpark data ingestion pipeline capable of parsing multi-line quoted CSVs and normalizing dirty tabular data.
2. **Spark Core & DataFrame Demonstration**: Explicitly implement Unit 3 concepts including RDD transformations (`map`, `filter`, `flatMap`, `reduceByKey`), DataFrame operations, lazy evaluation, and Catalyst optimization plans (`explain()`).
3. **Market Structure Analysis**: Quantify restaurant concentration across Bangalore localities and determine top cuisine market shares.
4. **Bivariate Correlation Analysis**: Compute Pearson correlation coefficients between dining expense, customer votes, and ratings while distinguishing correlation from causation.
5. **Advanced Visualization**: Address Unit 4 concepts by constructing statistical distributions, dual-axis comparative charts, spatial concentration Pareto models, and an advanced 2D Locality-versus-Cuisine heatmap.
6. **Interactive Presentation & Verification**: Develop a production-grade Streamlit interactive dashboard and an automated test suite verifying data transformations and analytical correctness.

---

## 5. Dataset Description & Schema

The dataset analyzed is the official **Zomato Bangalore Restaurants** dataset, comprising 51,717 raw records across 17 attributes.

### 5.1 Dataset Schema & Cleaned Data Types

| Attribute | Raw Type | Cleaned Spark Type | Description & Handling Strategy |
| :--- | :--- | :--- | :--- |
| `name` | String | `StringType` | Business trading name; normalized and trimmed. |
| `online_order` | String | `StringType` | Binary indicator (`Yes`/`No`) of delivery support. |
| `book_table` | String | `StringType` | Binary indicator (`Yes`/`No`) of reservation support. |
| `rate` | String | `DoubleType` | Extracted numerical rating from `'4.1/5'`. Unrated entries (`'NEW'`, `'-'`, null) converted to `null` to avoid distorting mean calculations. |
| `votes` | String/Int | `IntegerType` | Total customer reviews; non-numeric entries cast to 0. |
| `location` | String | `StringType` | Bangalore neighborhood; standardized for spatial grouping. |
| `rest_type` | String | `StringType` | Dining format (e.g., Casual Dining, Quick Bites, Cafe). |
| `cuisines` | String | `StringType` | Comma-separated list of culinary styles; tokenized via `flatMap` / `explode`. |
| `approx_cost(for two people)`| String | `DoubleType` | Average cost in INR; thousand commas stripped before numeric cast. |
| `listed_in(type)` | String | `StringType` | Dining category (Buffet, Delivery, Dine-out, Cafes). |
| `listed_in(city)` | String | `StringType` | Zomato search cluster zone. |

> **Critical Academic Integrity Note on Geospatial Data:**  
> The raw dataset contains detailed locality and street address strings but **no raw GPS latitude and longitude coordinates**. In accordance with rigorous scientific standards, no synthetic coordinates were fabricated. Geospatial analysis is conducted through locality-level spatial density, concentration percentiles, and commercial cluster profiling.

---

## 6. System Architecture & Methodology

```
+-----------------------------------------------------------------------------------+
|                            DATA INGESTION LAYER                                   |
|                      data/raw/zomato.csv (51,717 rows)                            |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     APACHE SPARK DISTRIBUTED PROCESSING ENGINE                     |
|  - JVM Modularity Configuration (Java 21 LTS)                                     |
|  - Schema Standardization & String Trimming                                       |
|  - Rating Parsing: '4.1/5' -> 4.1 | 'NEW'/'-' -> Null                             |
|  - Cost Parsing: '1,200' -> 1200.0                                                |
|  - Physical Entity Deduplication: [name, address, location]                       |
|    -> Retained: 12,519 Unique Physical Restaurants (39,177 duplicate listings dropped)|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         ANALYTICAL COMPUTATION ENGINE                             |
|  - Unit 3 RDD Operations: map(), filter(), flatMap(), reduceByKey()               |
|  - DataFrame Groupings: Locality ranking, Cuisine explode, Sample-threshold rating|
|  - Pearson Correlation: Cost vs Rating (r = +0.33), Votes vs Rating (r = +0.40)   |
|  - High-Dimensional Matrix: Locality x Cuisine Cross-Tabulation                   |
+-----------------------------------------------------------------------------------+
                                         |
                    +--------------------+--------------------+
                    |                                         |
                    v                                         v
+---------------------------------------+ +---------------------------------------+
|        VISUALIZATION LAYER            | |          DASHBOARD & VERIFICATION     |
| - Top 10 Localities Bar Chart         | | - Interactive Streamlit Application   |
| - Cuisine Volume vs Rating Dual Chart | |   (Dynamic Filters, Real-Time KPIs)   |
| - Cost vs Rating Bubble Scatter Plot  | | - Automated PyTest Test Suite         |
| - Advanced 2D Locality-Cuisine Heatmap| |   (11 Test Cases, 100% Pass Rate)     |
| - Spatial Pareto Concentration Curve  | |                                       |
+---------------------------------------+ +---------------------------------------+
```

---

## 7. Apache Spark Implementation & Unit 3 Concepts

### 7.1 Spark Core & RDD Operations
To demonstrate foundational concepts from Unit 3, the cleaning and analytical engine executed RDD operations directly on the cluster:
- **`rdd.filter(...)`**: Filtered out unrated records and empty location rows.
- **`rdd.map(...)`**: Mapped location records into `(locality, 1)` key-value pairs.
- **`rdd.reduceByKey(...)`**: Aggregated total counts by locality with map-side combining, avoiding high network shuffle overhead:
  - Whitefield: 887 restaurants
  - Electronic City: 730 restaurants
  - BTM: 729 restaurants
  - HSR: 706 restaurants
  - Marathahalli: 688 restaurants
- **`rdd.flatMap(...)`**: Split comma-separated cuisine strings into individual cuisine tokens across distributed worker nodes, counting North Indian (5,050), Chinese (3,600), South Indian (2,383), and Fast Food (2,129).

### 7.2 Spark Optimization Techniques
1. **Catalyst Query Plan Optimization**: The query execution plan was inspected using `.explain(mode='simple')`, confirming that filter operations (`Filter (isnotnull(location#...))`) are pushed to the earliest processing step before wide shuffles.
2. **In-Memory Caching**: The deduplicated, cleaned DataFrame was cached in memory (`cleaned_df.cache()`), preventing Spark from re-reading and re-parsing the raw 547 MB file for each of the 9 subsequent analytical aggregations.
3. **Partition Management**: Shuffle partitions were tuned to 8 (`spark.sql.shuffle.partitions = 8`) to align with local CPU hardware threads and eliminate partition scheduling overhead.

---

## 8. Results & Analytical Findings

### 8.1 Data Quality Audit
- **Raw Listings Ingested**: 51,717 rows.
- **Dropped Missing Identity Rows**: 21 rows (missing restaurant name or locality).
- **Duplicate Listings Dropped**: 39,177 rows (redundant search zone listings across delivery cities).
- **Unique Dining Entities Retained**: 12,519 restaurants.
- **Valid Customer Ratings**: 9,336 restaurants (74.57% completeness; 3,183 unrated/new venues preserved as null).
- **Valid Approximate Cost**: 12,469 restaurants (99.60% completeness).

### 8.2 Top Localities by Restaurant Concentration

| Rank | Locality | Restaurant Count | Average Rating (out of 5) | Average Cost for Two (₹) | Total Customer Votes |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | **Whitefield** | 887 | 3.63 | 557 | 102,689 |
| 2 | **Electronic City** | 730 | 3.56 | 496 | 45,785 |
| 3 | **BTM** | 729 | 3.64 | 400 | 126,589 |
| 4 | **HSR** | 706 | 3.68 | 491 | 114,357 |
| 5 | **Marathahalli** | 688 | 3.59 | 507 | 78,858 |
| 6 | **Indiranagar** | 621 | 3.84 | 698 | 321,942 |
| 7 | **JP Nagar** | 599 | 3.67 | 536 | 127,159 |
| 8 | **Bannerghatta Road** | 569 | 3.55 | 458 | 51,993 |
| 9 | **Bellandur** | 553 | 3.59 | 525 | 69,963 |
| 10 | **Jayanagar** | 545 | 3.77 | 473 | 148,822 |

*Insight:* While outer IT suburbs like Whitefield and Electronic City lead in raw restaurant counts, central cultural hubs like Indiranagar (3.84) and Jayanagar (3.77) achieve significantly higher customer satisfaction and review engagement.

### 8.3 Cuisine Popularity vs. Average Rating (Sample Size >= 30)
- **Highest Volume Cuisines**: North Indian (5,050 outlets), Chinese (3,600), South Indian (2,383), Fast Food (2,129), Biryani (1,762).
- **Top-Rated Cuisines (Min. 30 Outlets)**:
  1. Continental (3.89 / 5.0, 966 outlets)
  2. European (3.87 / 5.0, 114 outlets)
  3. Cafe (3.86 / 5.0, 942 outlets)
  4. Italian (3.83 / 5.0, 750 outlets)
  5. Desserts (3.79 / 5.0, 1,365 outlets)

*Insight:* High volume does not equate to high customer satisfaction. Mainstream staples (North Indian, Chinese) suffer from competitive quality dilution, while specialized dining categories maintain higher quality standards.

### 8.4 Statistical Correlations
- **Approximate Cost vs. Customer Rating**: $r = +0.3271$ (Moderate positive association).
- **Customer Votes vs. Customer Rating**: $r = +0.4001$ (Moderate positive association).
- **Approximate Cost vs. Customer Votes**: $r = +0.3397$ (Moderate positive association).

---

## 9. Visual Analytics & Interpretation (Unit 4)

### Visualization 1: Top 10 Bangalore Localities by Restaurant Concentration
![Top Localities Distribution](outputs/charts/01_top_localities_distribution.png)

- **Analytical Focus**: Evaluating spatial restaurant concentration.
- **Variables**: Categorical Locality (Y-axis) vs. Count of Unique Outlets (X-axis).
- **Interpretation**: Food service supply is heavily concentrated in major IT corridors (Whitefield, Electronic City) and student-dense residential zones (BTM, HSR). These top 10 localities host over 50% of all restaurants in Bangalore.

---

### Visualization 2: Cuisine Market Landscape — Volume vs. Customer Rating
![Cuisine Popularity vs Ratings](outputs/charts/02_cuisine_popularity_and_ratings.png)

- **Analytical Focus**: Comparing culinary supply volume against customer satisfaction.
- **Variables**: Outlet count (Left panel) vs. Mean customer rating with sample size filter $\ge 30$ (Right panel).
- **Interpretation**: The most common cuisines are not the highest rated. High-end specialty cuisines (Continental, European) achieve the highest ratings, reflecting higher culinary consistency and better dining ambiance.

---

### Visualization 3: Approximate Cost vs. Customer Rating
![Cost vs Rating Scatter](outputs/charts/03_cost_vs_rating_scatter.png)

- **Analytical Focus**: Testing the relationship between meal expense and customer sentiment.
- **Variables**: Approximate Cost for Two in INR (X-axis) vs. Rating (Y-axis) with linear regression fit.
- **Critical Caveat**: Pearson correlation ($r = +0.33$) indicates a positive association, not direct causality. Premium pricing enables investments in superior ingredients, chef training, and customer service, which drive higher ratings.

---

### Visualization 4 (Advanced): Locality vs. Cuisine Concentration Heatmap
![Advanced Locality Cuisine Heatmap](outputs/charts/05_advanced_locality_cuisine_heatmap.png)

- **Analytical Focus**: High-dimensional cross-tabulation of supply across commercial corridors.
- **Variables**: Top 10 Localities (Rows) $\times$ Top 10 Cuisines (Columns), color-encoded by restaurant count.
- **Interpretation**: North Indian and Chinese maintain ubiquitous presence across all zones. In contrast, South Indian and Fast Food exhibit intense spatial clustering in BTM (373 and 224 outlets respectively) and HSR, catering to dense student and young IT professional demographics.

---

### Visualization 5: Service Feature Availability Comparison
![Service Availability Comparison](outputs/charts/04_service_feature_comparison.png)

- **Analytical Focus**: Assessing the operational impact of online ordering and table booking.
- **Interpretation**: Venues offering table booking exhibit a significantly higher average rating (**4.15 vs. 3.65**) and generate over **6 times more review engagement** (842 average votes vs. 138 for non-booking). Table booking acts as an operational marker for organized casual and fine-dining venues.

---

### Visualization 6: Locality Spatial Concentration (Pareto Curve)
![Locality Spatial Concentration](outputs/charts/06_locality_spatial_concentration.png)

- **Analytical Focus**: Quantifying spatial inequality across Bangalore's dining market.
- **Interpretation**: The top 20 localities account for over 72% of all dining establishments in Bangalore, demonstrating an extreme geographic clustering around commercial belts.

---

## 10. Strategic Insights & Business Recommendations

1. **Market Saturation Strategy**: Prospective restaurateurs should avoid opening generic North Indian or Quick-Bite Chinese outlets in Whitefield or BTM due to severe market saturation. Opportunity exists in underserved premium niches (Cafes, Continental, Bakery/Desserts) in emerging residential zones.
2. **Digital Booking Adoption**: Food service businesses seeking to elevate their brand profile should enable table reservation capabilities. Table booking availability is strongly associated with high customer engagement and above-average ratings ($4.15$).
3. **Data Quality Governance**: Commercial aggregators like Zomato must implement strict schema validation at the data collection stage to avoid storing multi-value string formats (e.g., `'4.1/5'`) and embedded commas in numerical fields.

---

## 11. Challenges & Limitations

1. **Absence of Raw Geographic Coordinates**: The raw dataset lacks GPS coordinates, preventing point-level GIS radius analysis or routing optimization.
2. **Review Aggregation Bias**: The dataset provides aggregate vote counts and rating snapshots rather than timestamped customer transactions, limiting longitudinal time-series forecasting.
3. **Multi-Listing Redundancy**: Restaurants listed across adjacent delivery zones create substantial duplication, requiring explicit deduplication prior to entity-level analysis.

---

## 12. Conclusion

This project successfully implemented an end-to-end Big Data Analytics workflow on the Zomato Bangalore Restaurants dataset using Apache Spark and modern data visualization frameworks. By combining Spark Core RDD transformations, DataFrame Catalyst optimizations, and advanced visual analytics, we answered all required business questions and uncovered significant structural patterns in Bangalore's restaurant landscape. The complete reproducibility of the codebase—validated via automated tests and an interactive dashboard—ensures compliance with the academic and practical standards of the FA2 evaluation rubric.

---

## 13. References

1. Zaharia, M., et al. (2016). *Apache Spark: A Unified Engine for Big Data Processing.* Communications of the ACM.
2. Armbrust, M., et al. (2015). *Spark SQL: Relational Data Processing in Spark.* ACM SIGMOD.
3. Few, S. (2009). *Now You See It: Simple Visualization Techniques for Quantitative Analysis.* Analytics Press.
4. Kaggle Repository: *Zomato Bangalore Restaurants Dataset*.
