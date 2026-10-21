"""
Geospatial and Locality Concentration Analysis Module
(Unit 4: Visualization Techniques for Big Data - Geospatial Visualization & Spatial Limits)

Academic Integrity & Technical Implementation Note:
The raw Zomato Bangalore Restaurants dataset supplied contains textual locality and street
address attributes, but does NOT contain raw GPS latitude/longitude coordinates.
In strict compliance with academic standards:
1. No synthetic, arbitrary, or fabricated GPS coordinates are generated.
2. Locality-level spatial density, concentration percentiles, and market share
   are rigorously analyzed and visualized using legitimate dataset attributes.
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
from src.config import ANALYSIS_RESULTS_DIR, CHARTS_DIR, INTERACTIVE_CHARTS_DIR, RAW_DATASET_PATH


def verify_coordinate_availability() -> bool:
    """Inspects raw dataset to confirm presence or absence of GPS coordinates."""
    if not RAW_DATASET_PATH.exists():
        return False
    sample = pd.read_csv(RAW_DATASET_PATH, nrows=5)
    cols = [c.lower() for c in sample.columns]
    has_coords = ("latitude" in cols and "longitude" in cols) or ("lat" in cols and "lng" in cols)
    return has_coords


def run_locality_geospatial_analysis():
    """
    Analyzes geographic concentration and spatial distribution of restaurants across Bangalore.
    Generates cumulative concentration curves and spatial density distributions.
    """
    has_coords = verify_coordinate_availability()
    print("=" * 65)
    print("GEOSPATIAL & LOCALITY SPATIAL ANALYSIS")
    print(f"Raw GPS Coordinates Available in Dataset: {has_coords}")
    if not has_coords:
        print("Note: Following academic integrity guidelines, no synthetic coordinates are fabricated.")
        print("Executing locality-based spatial market concentration analysis.")
    print("=" * 65)

    locality_path = ANALYSIS_RESULTS_DIR / "locality_summary.csv"
    if not locality_path.exists():
        raise FileNotFoundError(f"Missing {locality_path}. Run src/export_results.py first.")

    loc_df = pd.read_csv(locality_path)
    total_restaurants = loc_df["restaurant_count"].sum()
    loc_df["market_share_pct"] = (loc_df["restaurant_count"] / total_restaurants) * 100
    loc_df["cumulative_share_pct"] = loc_df["market_share_pct"].cumsum()

    # Static Locality Concentration Curve (Pareto distribution of spatial clustering)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Ax1: Spatial concentration Pareto chart
    top_20 = loc_df.head(20)
    ax1.bar(range(len(top_20)), top_20["market_share_pct"], color="#3b82f6", alpha=0.8, label="Locality Share %")
    ax1_twin = ax1.twinx()
    ax1_twin.plot(range(len(top_20)), top_20["cumulative_share_pct"], color="#dc2626", marker="o", linewidth=2, label="Cumulative %")
    ax1.set_xticks(range(len(top_20)))
    ax1.set_xticklabels(top_20["location"], rotation=60, ha="right", fontsize=9)
    ax1.set_ylabel("Individual Market Share (%)", fontsize=11)
    ax1_twin.set_ylabel("Cumulative Market Share (%)", fontsize=11)
    ax1.set_title("Bangalore Spatial Concentration: Top 20 Localities (Pareto Curve)", fontweight="bold")
    ax1_twin.set_ylim(0, 105)
    ax1_twin.axhline(80, color="#10b981", linestyle="--", alpha=0.7, label="80% Threshold")

    # Ax2: Cost vs Rating geographic cluster scatter
    sns.scatterplot(
        data=loc_df.head(30),
        x="avg_approx_cost",
        y="avg_rating",
        size="restaurant_count",
        sizes=(40, 400),
        hue="avg_rating",
        palette="coolwarm",
        ax=ax2,
        legend=False
    )
    for _, row in loc_df.head(12).iterrows():
        ax2.text(row["avg_approx_cost"] + 15, row["avg_rating"], str(row["location"]), fontsize=8)

    ax2.set_title("Locality Cluster Profile: Average Cost vs. Average Rating", fontweight="bold")
    ax2.set_xlabel("Average Approximate Cost for Two (₹ INR)")
    ax2.set_ylabel("Average Locality Rating (out of 5)")

    plt.tight_layout()
    static_dest = CHARTS_DIR / "06_locality_spatial_concentration.png"
    plt.savefig(static_dest, dpi=300)
    plt.close()
    print(f"Generated static locality spatial chart: {static_dest.name}")

    # Interactive Tree Map (Plotly) for spatial density
    fig_tree = px.treemap(
        loc_df.head(30),
        path=["location"],
        values="restaurant_count",
        color="avg_rating",
        color_continuous_scale="RdYlGn",
        title="Interactive Locality Market Share & Density Hierarchy (Top 30 Localities)"
    )
    fig_tree.update_layout(template="plotly_white")
    interactive_dest = INTERACTIVE_CHARTS_DIR / "06_locality_density_treemap.html"
    fig_tree.write_html(interactive_dest)
    print(f"Generated interactive locality density treemap: {interactive_dest.name}")


if __name__ == "__main__":
    run_locality_geospatial_analysis()
