"""
Standalone Chart Generation Module (Unit 4: Visualization Techniques for Big Data)
Generates static (Matplotlib/Seaborn) and interactive (Plotly) visualizations:
1. Top Localities Restaurant Distribution (Horizontal Bar Chart)
2. Cuisine Popularity vs Ratings (Comparative Chart)
3. Cost vs Rating with Votes as Bubble Size (Scatter Plot)
4. Rating Distribution (Histogram/Bar Chart)
5. Service Availability Impact: Online Ordering & Table Booking (Grouped Bars)
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from src.config import (
    ANALYSIS_RESULTS_DIR, CHARTS_DIR, INTERACTIVE_CHARTS_DIR,
    CLEANED_DATASET_CSV
)

# Style configuration for clean academic presentation
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def plot_top_localities():
    """Visualization 1: Top 10 Bangalore Localities by Restaurant Count."""
    filepath = ANALYSIS_RESULTS_DIR / "locality_summary.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing analysis file: {filepath}. Run src/export_results.py first.")

    df = pd.read_csv(filepath).head(10).sort_values("restaurant_count", ascending=True)

    # Static Matplotlib/Seaborn Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df["location"], df["restaurant_count"], color="#e23744", edgecolor="#990000", alpha=0.85)
    ax.set_title("Top 10 Bangalore Localities by Restaurant Concentration", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Unique Restaurants", fontsize=12, labelpad=10)
    ax.set_ylabel("Bangalore Locality", fontsize=12)

    # Add data value labels
    for bar in bars:
        ax.text(
            bar.get_width() + 15, bar.get_y() + bar.get_height() / 2,
            f"{int(bar.get_width()):,}",
            va="center", ha="left", fontsize=10, fontweight="semibold", color="#333333"
        )

    plt.tight_layout()
    static_dest = CHARTS_DIR / "01_top_localities_distribution.png"
    plt.savefig(static_dest, dpi=300)
    plt.close()
    print(f"Generated static chart: {static_dest.name}")

    # Interactive Plotly Chart
    fig_interactive = px.bar(
        df,
        x="restaurant_count",
        y="location",
        orientation="h",
        text="restaurant_count",
        title="Top 10 Bangalore Localities by Restaurant Density",
        labels={"restaurant_count": "Restaurant Count", "location": "Locality"},
        color="avg_rating",
        color_continuous_scale="Reds",
        hover_data=["avg_rating", "total_votes", "avg_approx_cost"]
    )
    fig_interactive.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))
    interactive_dest = INTERACTIVE_CHARTS_DIR / "01_top_localities_distribution.html"
    fig_interactive.write_html(interactive_dest)
    print(f"Generated interactive chart: {interactive_dest.name}")


def plot_cuisine_popularity_and_ratings():
    """Visualization 2: Cuisine Popularity vs Ratings (Thresholded)."""
    pop_path = ANALYSIS_RESULTS_DIR / "cuisine_popularity.csv"
    rate_path = ANALYSIS_RESULTS_DIR / "cuisine_ratings_thresholded.csv"

    if not pop_path.exists() or not rate_path.exists():
        raise FileNotFoundError("Missing cuisine analysis files. Run src/export_results.py first.")

    pop_df = pd.read_csv(pop_path).head(10).sort_values("restaurant_count", ascending=True)
    rate_df = pd.read_csv(rate_path).head(10).sort_values("avg_rating", ascending=True)

    # Static Dual Chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Ax1: Volume
    ax1.barh(pop_df["cuisine_item"], pop_df["restaurant_count"], color="#3b82f6", alpha=0.85)
    ax1.set_title("Most Common Cuisines (Restaurant Count)", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Number of Restaurants", fontsize=11)
    for i, v in enumerate(pop_df["restaurant_count"]):
        ax1.text(v + 50, i, f"{v:,}", va="center", fontsize=9)

    # Ax2: Quality (Ratings with sample size threshold >= 30)
    ax2.barh(rate_df["cuisine_item"], rate_df["avg_rating"], color="#10b981", alpha=0.85)
    ax2.set_xlim(3.0, 5.0)
    ax2.set_title("Top Rated Cuisines (Min. 30 Restaurants)", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Average Rating (out of 5)", fontsize=11)
    for i, v in enumerate(rate_df["avg_rating"]):
        ax2.text(v + 0.03, i, f"{v:.2f}", va="center", fontsize=9)

    plt.suptitle("Cuisine Landscape: Volume vs. Customer Rating Performance", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    static_dest = CHARTS_DIR / "02_cuisine_popularity_and_ratings.png"
    plt.savefig(static_dest, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated static chart: {static_dest.name}")

    # Interactive Plotly Chart
    fig_interactive = px.scatter(
        pd.read_csv(rate_path),
        x="restaurant_count",
        y="avg_rating",
        size="total_votes",
        text="cuisine_item",
        hover_name="cuisine_item",
        title="Cuisine Position Matrix: Market Share vs. Average Rating (Sample >= 30)",
        labels={"restaurant_count": "Restaurant Count", "avg_rating": "Average Rating (out of 5)"},
        color="avg_rating",
        color_continuous_scale="Viridis"
    )
    fig_interactive.update_traces(textposition="top center")
    fig_interactive.update_layout(template="plotly_white")
    interactive_dest = INTERACTIVE_CHARTS_DIR / "02_cuisine_popularity_and_ratings.html"
    fig_interactive.write_html(interactive_dest)
    print(f"Generated interactive chart: {interactive_dest.name}")


def plot_cost_vs_rating():
    """Visualization 3: Approximate Cost vs Customer Rating Scatter Plot."""
    if not CLEANED_DATASET_CSV.exists():
        raise FileNotFoundError(f"Missing {CLEANED_DATASET_CSV}. Run src/export_results.py first.")

    # Load cleaned dataset sample for high-clarity plotting
    df = pd.read_csv(CLEANED_DATASET_CSV)
    df_valid = df.dropna(subset=["rating_num", "approx_cost_num"])

    # Sample up to 2500 points for readable static scatter plot
    plot_sample = df_valid.sample(min(2500, len(df_valid)), random_state=42)

    # Static Scatter Plot with Regression Trendline
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.regplot(
        data=plot_sample,
        x="approx_cost_num",
        y="rating_num",
        scatter_kws={"alpha": 0.45, "color": "#2563eb", "s": 30},
        line_kws={"color": "#dc2626", "linewidth": 2},
        ax=ax
    )
    ax.set_title("Relationship Between Approximate Cost (for Two) and Customer Rating", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Approximate Cost for Two People (₹ INR)", fontsize=11)
    ax.set_ylabel("Customer Rating (Scale: 1.0 - 5.0)", fontsize=11)
    ax.set_xlim(0, 4000)
    ax.set_ylim(1.8, 5.1)

    # Add academic disclaimer annotation regarding correlation vs causation
    ax.text(
        0.03, 0.05,
        "Note: Positive Pearson correlation (r ≈ +0.33) indicates association,\nnot direct causality between price and quality.",
        transform=ax.transAxes, fontsize=9,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fef3c7", edgecolor="#f59e0b", alpha=0.9)
    )

    plt.tight_layout()
    static_dest = CHARTS_DIR / "03_cost_vs_rating_scatter.png"
    plt.savefig(static_dest, dpi=300)
    plt.close()
    print(f"Generated static chart: {static_dest.name}")

    # Interactive Bubble Plot (Plotly)
    fig_interactive = px.scatter(
        plot_sample.head(1000),
        x="approx_cost_num",
        y="rating_num",
        size="votes_num",
        color="online_order",
        hover_name="name",
        hover_data=["location", "cuisines"],
        title="Interactive Cost vs. Rating Scatter Plot (Bubble Size = Total Votes)",
        labels={
            "approx_cost_num": "Cost for Two (₹)",
            "rating_num": "Rating (out of 5)",
            "online_order": "Online Ordering"
        },
        color_discrete_map={"Yes": "#10b981", "No": "#ef4444"}
    )
    fig_interactive.update_layout(template="plotly_white")
    interactive_dest = INTERACTIVE_CHARTS_DIR / "03_cost_vs_rating_scatter.html"
    fig_interactive.write_html(interactive_dest)
    print(f"Generated interactive chart: {interactive_dest.name}")


def plot_service_availability_comparison():
    """Visualization 5: Impact of Online Ordering and Table Booking on Ratings and Votes."""
    online_path = ANALYSIS_RESULTS_DIR / "online_order_comparison.csv"
    table_path = ANALYSIS_RESULTS_DIR / "table_booking_comparison.csv"

    if not online_path.exists() or not table_path.exists():
        raise FileNotFoundError("Missing service comparison analysis files. Run src/export_results.py first.")

    online_df = pd.read_csv(online_path)
    table_df = pd.read_csv(table_path)

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Online Order vs Avg Rating
    ax1.bar(online_df["online_order"], online_df["avg_rating"], color=["#f87171", "#34d399"], width=0.5)
    ax1.set_ylim(3.0, 4.5)
    ax1.set_title("Online Ordering vs Average Rating", fontweight="bold")
    ax1.set_ylabel("Average Rating")
    for i, v in enumerate(online_df["avg_rating"]):
        ax1.text(i, v + 0.04, f"{v:.2f}", ha="center", fontweight="semibold")

    # 2. Online Order vs Avg Votes
    ax2.bar(online_df["online_order"], online_df["avg_votes"], color=["#f87171", "#34d399"], width=0.5)
    ax2.set_title("Online Ordering vs Average Engagement (Votes)", fontweight="bold")
    ax2.set_ylabel("Average Customer Votes")
    for i, v in enumerate(online_df["avg_votes"]):
        ax2.text(i, v + 15, f"{v:.1f}", ha="center", fontweight="semibold")

    # 3. Table Booking vs Avg Rating
    ax3.bar(table_df["book_table"], table_df["avg_rating"], color=["#93c5fd", "#6366f1"], width=0.5)
    ax3.set_ylim(3.0, 4.5)
    ax3.set_title("Table Booking vs Average Rating", fontweight="bold")
    ax3.set_ylabel("Average Rating")
    for i, v in enumerate(table_df["avg_rating"]):
        ax3.text(i, v + 0.04, f"{v:.2f}", ha="center", fontweight="semibold")

    # 4. Table Booking vs Avg Votes
    ax4.bar(table_df["book_table"], table_df["avg_votes"], color=["#93c5fd", "#6366f1"], width=0.5)
    ax4.set_title("Table Booking vs Average Engagement (Votes)", fontweight="bold")
    ax4.set_ylabel("Average Customer Votes")
    for i, v in enumerate(table_df["avg_votes"]):
        ax4.text(i, v + 25, f"{v:.1f}", ha="center", fontweight="semibold")

    plt.suptitle("Comparative Analysis of Feature Availability (Online Ordering & Table Booking)", fontsize=14, fontweight="bold", y=1.00)
    plt.tight_layout()
    static_dest = CHARTS_DIR / "04_service_feature_comparison.png"
    plt.savefig(static_dest, dpi=300)
    plt.close()
    print(f"Generated static chart: {static_dest.name}")


def generate_all_charts():
    """Generates all standard Big Data visualizations."""
    print("=" * 60)
    print("GENERATING VISUALIZATIONS (Unit 4: Big Data Visualization)")
    print("=" * 60)
    plot_top_localities()
    plot_cuisine_popularity_and_ratings()
    plot_cost_vs_rating()
    plot_service_availability_comparison()
    print("\nStandard chart generation complete! Outputs in 'outputs/charts/' and 'outputs/interactive_charts/'")


if __name__ == "__main__":
    generate_all_charts()
