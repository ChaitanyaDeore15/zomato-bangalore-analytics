"""
Advanced Visualization Module: Locality vs Cuisine Density Heatmap
(Unit 4: Visualization Techniques for Big Data - Heatmaps & High-Dimensional Matrices)

Demonstrates cross-dimensional distribution of restaurant supply across Bangalore's
primary commercial zones and leading cuisine styles.
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
from src.config import ANALYSIS_RESULTS_DIR, CHARTS_DIR, INTERACTIVE_CHARTS_DIR


def generate_locality_cuisine_heatmap():
    """
    Loads Spark-generated locality-by-cuisine pivot matrix and renders
    both high-resolution static and interactive heatmaps.
    """
    matrix_path = ANALYSIS_RESULTS_DIR / "locality_cuisine_matrix.csv"
    if not matrix_path.exists():
        raise FileNotFoundError(
            f"Missing {matrix_path}. Please execute 'python src/export_results.py' first."
        )

    # Load matrix: rows = location, columns = top cuisines
    matrix_df = pd.read_csv(matrix_path)
    if "location" in matrix_df.columns:
        matrix_df = matrix_df.set_index("location")

    # Static Heatmap using Seaborn
    plt.figure(figsize=(12, 8))
    sns.set_theme(style="white")

    ax = sns.heatmap(
        matrix_df,
        annot=True,
        fmt="d",
        cmap="YlOrRd",
        linewidths=0.7,
        linecolor="#ffffff",
        cbar_kws={"label": "Number of Restaurants Offering Cuisine"}
    )

    plt.title(
        "Advanced Big Data Heatmap: Locality vs. Cuisine Concentration Matrix\n(Top 10 Localities × Top 10 Cuisines in Bangalore)",
        fontsize=14,
        fontweight="bold",
        pad=18
    )
    plt.xlabel("Cuisine Category", fontsize=12, labelpad=10)
    plt.ylabel("Bangalore Commercial Locality", fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)

    plt.tight_layout()
    static_dest = CHARTS_DIR / "05_advanced_locality_cuisine_heatmap.png"
    plt.savefig(static_dest, dpi=300)
    plt.close()
    print(f"Generated static advanced heatmap: {static_dest.name}")

    # Interactive Plotly Heatmap
    fig_interactive = px.imshow(
        matrix_df,
        labels=dict(x="Cuisine Category", y="Locality", color="Restaurant Count"),
        x=matrix_df.columns,
        y=matrix_df.index,
        color_continuous_scale="YlOrRd",
        text_auto=True,
        title="Interactive Advanced Heatmap: Cuisine Supply Density across Bangalore Localities"
    )
    fig_interactive.update_layout(
        template="plotly_white",
        margin=dict(l=50, r=50, t=60, b=50),
        xaxis_tickangle=-45
    )
    interactive_dest = INTERACTIVE_CHARTS_DIR / "05_advanced_locality_cuisine_heatmap.html"
    fig_interactive.write_html(interactive_dest)
    print(f"Generated interactive advanced heatmap: {interactive_dest.name}")


if __name__ == "__main__":
    generate_locality_cuisine_heatmap()
