# Academic Viva Preparation: Zomato Bangalore Restaurant Analytics
**Subject:** Big Data Analytics (FA2 Activity)  
**Student Name:** Himanshu Poddar  
**Coverage:** Unit 3 (Apache Spark Frameworks) & Unit 4 (Visualization Techniques for Big Data)

---

### Q1: Why was Apache Spark selected over traditional tools like Pandas or MapReduce?
**Answer:**  
Apache Spark was selected because it provides in-memory distributed computing, which is up to 100 times faster than disk-bound Hadoop MapReduce. Unlike Pandas, which is single-threaded and constrained by single-node RAM (leading to Out-Of-Memory errors on massive multi-gigabyte files), Spark operates on distributed data abstractions (RDDs and DataFrames) with lazy evaluation and Catalyst query optimization, allowing it to scale seamlessly from local laptops to multi-node enterprise clusters.

---

### Q2: What is Spark Core and what role does it play?
**Answer:**  
Spark Core is the foundational underlying execution engine of the Apache Spark platform. It provides distributed task dispatching, in-memory scheduling, basic I/O functionalities, fault tolerance, and memory management. All higher-level libraries—including Spark SQL, Spark Streaming, and MLlib—are built on top of Spark Core.

---

### Q3: What is a Resilient Distributed Dataset (RDD)?
**Answer:**  
An RDD is Spark’s fundamental, low-level data abstraction. It is an immutable, partitioned collection of elements that can be processed in parallel across cluster nodes. It is "Resilient" because it maintains a lineage graph (DAG) enabling automatic recomputation of lost partitions upon failure, "Distributed" across memory across nodes, and a "Dataset" holding records.

---

### Q4: What is the key difference between an RDD and a DataFrame?
**Answer:**  
- **RDD**: Schema-unaware collection of raw Java/Python objects. It provides fine-grained procedural control (`map`, `flatMap`, `reduceByKey`), but Spark cannot inspect the internal structure of the data, so it cannot optimize execution plans automatically.
- **DataFrame**: A distributed collection of data organized into named columns (like a relational database table). It is schema-aware and allows the Catalyst Optimizer to perform logical query optimization, predicate pushdown, and tungsten code generation.

---

### Q5: What is the difference between Spark Transformations and Actions?
**Answer:**  
- **Transformations** (`map`, `filter`, `flatMap`, `groupBy`, `select`) create a new dataset from an existing one. They are **lazy** and do not execute immediately; they simply append operations to the execution Directed Acyclic Graph (DAG).
- **Actions** (`count`, `collect`, `take`, `saveAsTextFile`, `show`) trigger the actual computation of the DAG across the cluster and return a result to the driver or write data to storage.

---

### Q6: What is Lazy Evaluation and why is it beneficial?
**Answer:**  
Lazy evaluation means that Spark does not execute transformations the moment they are declared. Instead, Spark builds up a lineage graph of transformations. Computation only occurs when an action is called. This enables Spark’s Catalyst Optimizer to inspect the entire query pipeline, combine adjacent operations, eliminate unnecessary columns, push filters down to the data source level, and minimize expensive disk and network I/O.

---

### Q7: What is the difference between `map()` and `flatMap()` in RDD processing?
**Answer:**  
- `map(func)` applies a 1-to-1 transformation, returning an RDD with the exact same number of elements as the input.
- `flatMap(func)` applies a 1-to-many transformation, where each input element can be mapped to 0, 1, or multiple output elements, and flattens the resulting collections.  
*In this project*, `flatMap` was used to split comma-separated cuisine strings (e.g., `"North Indian, Chinese"`) into distinct individual cuisine tokens.

---

### Q8: How does `reduceByKey()` work and why is it preferred over `groupByKey()`?
**Answer:**  
`reduceByKey(func)` combines values with the same key using an associative and commutative reduce function. It performs map-side aggregation (a local combiner step) before shuffling data across the network, drastically reducing data transfer. In contrast, `groupByKey()` shuffles all raw values across the network without combining, leading to severe network bottlenecks and out-of-memory errors.

---

### Q9: What are Narrow and Wide dependencies in Apache Spark?
**Answer:**  
- **Narrow Dependency**: Each partition of the parent RDD is used by at most one partition of the child RDD (e.g., `map()`, `filter()`). No network shuffle is required; execution occurs locally in pipeline fashion.
- **Wide Dependency**: Multiple child partitions depend on data from a single parent partition (e.g., `reduceByKey()`, `groupBy()`, `join()`). This necessitates a **shuffle** operation, transferring data across cluster nodes over the network, which introduces synchronization barriers.

---

### Q10: What is an execution plan in Spark and how do you inspect it?
**Answer:**  
An execution plan represents the sequence of physical and logical steps Spark will execute to fulfill a query. It can be inspected by invoking `.explain(mode='simple')` or `.explain(mode='extended')` on any DataFrame. It displays the Parsed Logical Plan, Analyzed Logical Plan, Optimized Logical Plan (Catalyst), and Physical Plan, highlighting partition pruning, hash aggregates, and exchange operations.

---

### Q11: When should you use Spark Caching / Persistence?
**Answer:**  
Caching (`df.cache()` or `df.persist()`) should be used when an intermediate DataFrame or RDD is accessed repeatedly by multiple downstream actions. In our pipeline, the cleaned dataset (`cleaned_df`) was cached in memory because it served as the single source for 9 distinct downstream analytical aggregations. Caching prevents Spark from re-evaluating the upstream raw CSV reading and cleaning pipeline 9 separate times.

---

### Q12: Why did we drop duplicates on `[name, address, location]`?
**Answer:**  
In the raw Zomato dataset, restaurants are listed multiple times because Zomato creates duplicate entries for different delivery search zones (`listed_in(city)`). If an analyst computes average restaurant ratings or cost directly on the raw 51,717 rows, multi-listed restaurants are heavily overcounted. Deduplicating on primary physical identity `[name, address, location]` yielded 12,519 unique establishments, ensuring accurate restaurant-level entity analytics.

---

### Q13: How were invalid ratings like `'NEW'`, `'-'`, or null handled during data cleaning?
**Answer:**  
They were converted to `null` (`None` in Python / `null` in PySpark) rather than imputed with `0.0`. If unrated restaurants or new openings are imputed with 0, the empirical rating mean drops artificially from ~3.70 to ~2.10, severely skewing statistical distributions, regressions, and correlation metrics. Preserving them as null ensures unrated establishments are excluded only from rating-specific computations.

---

### Q14: How were the approximate cost values cleaned?
**Answer:**  
The raw column `approx_cost(for two people)` stored monetary amounts as strings with embedded thousand-separator commas (e.g., `'1,200'`). Using Spark SQL's `F.regexp_replace(F.trim(F.col(...)), ",", "")`, commas were removed before casting the clean string to `DoubleType`.

---

### Q15: Why is a minimum sample-size threshold critical when ranking cuisines?
**Answer:**  
Without a sample-size threshold, rare or obscure cuisines with only 1 or 2 restaurants that happened to receive a single 5.0 rating would erroneously top the city-wide leaderboard. By enforcing `min_restaurants = 30`, we ensure rankings represent statistically defensible customer sentiment rather than small-sample noise.

---

### Q16: What does the advanced Locality-versus-Cuisine Heatmap demonstrate?
**Answer:**  
The advanced heatmap (Unit 4: High-Dimensional Visualizations) cross-tabulates Bangalore's top 10 commercial dining hubs against the top 10 cuisines. It reveals market density patterns—showing that while North Indian and Chinese have ubiquitous presence across all sectors, Fast Food and South Indian cluster intensely in student and residential hubs (BTM, HSR, Electronic City).

---

### Q17: Why was geospatial analysis conducted via locality concentration rather than GPS coordinates?
**Answer:**  
The raw Zomato dataset contains textual addresses and locality names, but completely lacks latitude and longitude coordinates. Academic integrity dictates that synthetic coordinates must never be fabricated. Therefore, spatial distribution was analyzed through locality density aggregations, market share percentiles, and Pareto concentration curves rather than an unverified coordinate map.

---

### Q18: What is the correlation between approximate cost and customer rating, and how do we interpret it?
**Answer:**  
The Pearson correlation between approximate cost and rating is **r ≈ +0.33**, representing a weak-to-moderate positive association. Crucially, **correlation does not imply causation**. Paying higher prices does not guarantee high quality; rather, higher-priced venues generally possess greater capital to invest in premium culinary talent, ambiance, hygiene, and hospitality.

---

### Q19: What are the primary business insights discovered from the data?
**Answer:**  
1. **Spatial Hubs**: Whitefield (887), Electronic City (730), and BTM (729) host the largest concentration of restaurants.
2. **Cuisine Saturation**: North Indian (5,050 outlets) and Chinese (3,600 outlets) represent the most saturated segments.
3. **Service Features**: Restaurants offering table booking have significantly higher ratings (4.15 vs 3.65) and over 6x more customer votes, indicating that reservation capability is a hallmark of high-engagement dining.

---

### Q20: How would this architecture scale if live streaming data were introduced?
**Answer:**  
The batch pipeline would transition to **Spark Structured Streaming**. New incoming orders, ratings, and reviews from Kafka topics would be ingested in micro-batches or continuous processing mode. Windowed aggregations (e.g., 10-minute sliding windows) would update real-time metrics, writing to a low-latency sink like Delta Lake or Redis, which the Streamlit dashboard would poll for live operational monitoring.
