# Data Dictionary: Zomato Bangalore Restaurants Dataset

| Column Name | Raw Data Type | Cleaned Spark Data Type | Description | Sample Raw Values | Cleaning & Handling Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `url` | String | String | Permanent URL of the restaurant profile on Zomato | `https://www.zomato.com/...` | Retained as unique external identifier; trimmed. |
| `address` | String | String | Complete postal/street address of the restaurant | `942, 21st Main Road, 2nd Stage...` | Trimmed whitespace and standard string cleaning. |
| `name` | String | String | Business trading name of the restaurant | `Jalsa`, `Spice Elephant` | Normalized casing, trimmed extra spaces. |
| `online_order` | String | String (`Yes`/`No`) | Flag indicating if online delivery ordering is accepted | `Yes`, `No` | Standardized to categorical binary (`Yes` / `No`). |
| `book_table` | String | String (`Yes`/`No`) | Flag indicating table reservation service | `Yes`, `No` | Standardized to categorical binary (`Yes` / `No`). |
| `rate` | String | Double (`rating_num`) | Customer rating on a 5-point scale | `4.1/5`, `NEW`, `-`, null | Parsed `/5` suffix, stripped whitespace. `NEW`, `-`, and invalid entries are converted to `null` to avoid skewing numerical statistics (never imputed as 0.0). |
| `votes` | Integer / String | Integer (`votes`) | Aggregated count of user reviews/ratings submitted | `775`, `0`, `487` | Cast to integer; missing/unparseable set to 0. |
| `phone` | String | String | Contact telephone numbers | `080 42297555\n+91 9743772233` | Raw metadata string. |
| `location` | String | String (`location`) | Specific neighborhood / locality in Bangalore | `Banashankari`, `BTM`, `Koramangala 5th Block` | Trimmed, normalized, used for geographic grouping. Note: raw dataset does NOT have latitude/longitude. |
| `rest_type` | String | String (`rest_type`) | Type of food establishment | `Casual Dining`, `Quick Bites`, `Cafe` | Cleaned and tokenized for multi-category analysis. |
| `dish_liked` | String | String | Popular customer-recommended dishes | `Pasta, Dum Biryani` | High missingness (~50%); preserved where available. |
| `cuisines` | String | String (`cuisines`) | Comma-separated list of culinary styles | `North Indian, Mughlai, Chinese` | Trimmed, split into individual items via Spark `flatMap` / `explode` for granular cuisine metrics. |
| `approx_cost(for two people)` | String | Double (`approx_cost`) | Estimated average spend for two people in INR (₹) | `800`, `1,200`, `2,500` | Removed thousand-separator commas (`,`), trimmed, cast to `DoubleType`. Nulls preserved. |
| `reviews_list` | String | String | Array of rating-review text tuples | `[('Rated 4.0', '...'), ...]` | High volume text, maintained for reference or filtered for light memory usage. |
| `menu_item` | String | String | Array of items listed on restaurant menu | `[]`, `['Veg Roll', ...]` | Array text string. |
| `listed_in(type)` | String | String (`meal_type`) | High-level dining category | `Buffet`, `Delivery`, `Dine-out`, `Cafes` | Cleaned categorical field. |
| `listed_in(city)` | String | String (`city_zone`) | Zomato Bangalore administrative cluster | `Banashankari`, `Bannerghatta Road` | Zone/cluster classification. |

## Key Data Quality Observations:
1. **Latitude/Longitude**: Not present in raw dataset. Academic integrity guideline: no fictional coordinates are fabricated; locality-based spatial aggregation and heatmap analysis are utilized.
2. **Ratings**: Many unrated or newly opened restaurants have `'NEW'` or `'-'`. Imputing these with 0 would dramatically distort mean ratings from 3.7 to ~2.1. Spark pipeline cleanly models them as `None`/`Null`.
3. **Approximate Cost**: Format includes commas (`1,500`). Regex/string replace is required prior to numeric casting.
4. **Duplicate Records**: Restaurants listed across multiple city search clusters (`listed_in(city)`) share identical `name`, `address`, and `phone`. De-duplication strategies must consider whether analysis is at unique restaurant level or listing level.
