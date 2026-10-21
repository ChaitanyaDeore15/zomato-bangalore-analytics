"""
Unit Tests for Visualizations and Output File Integrity
"""

import sys
from pathlib import Path
import pytest
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    CHARTS_DIR,
    INTERACTIVE_CHARTS_DIR,
    ANALYSIS_RESULTS_DIR,
    CLEANED_DATASET_CSV
)


def test_generated_static_charts_exist_and_non_empty():
    """Ensures all 6 static PNG chart files were generated and have non-zero file sizes."""
    expected_charts = [
        "01_top_localities_distribution.png",
        "02_cuisine_popularity_and_ratings.png",
        "03_cost_vs_rating_scatter.png",
        "04_service_feature_comparison.png",
        "05_advanced_locality_cuisine_heatmap.png",
        "06_locality_spatial_concentration.png"
    ]
    for filename in expected_charts:
        chart_path = CHARTS_DIR / filename
        assert chart_path.exists(), f"Missing static chart: {filename}"
        assert chart_path.stat().st_size > 10000, f"Chart file {filename} is suspiciously small."


def test_generated_interactive_charts_exist():
    """Ensures interactive HTML visualizations exist."""
    expected_html = [
        "01_top_localities_distribution.html",
        "02_cuisine_popularity_and_ratings.html",
        "03_cost_vs_rating_scatter.html",
        "05_advanced_locality_cuisine_heatmap.html",
        "06_locality_density_treemap.html"
    ]
    for filename in expected_html:
        html_path = INTERACTIVE_CHARTS_DIR / filename
        assert html_path.exists(), f"Missing interactive chart: {filename}"
        assert html_path.stat().st_size > 50000, f"Interactive file {filename} is suspiciously small."


def test_analysis_result_tables_integrity():
    """Verifies that key analysis CSV tables have valid content and required columns."""
    locality_file = ANALYSIS_RESULTS_DIR / "locality_summary.csv"
    assert locality_file.exists()
    loc_df = pd.read_csv(locality_file)
    assert "location" in loc_df.columns
    assert "restaurant_count" in loc_df.columns
    assert len(loc_df) > 0

    matrix_file = ANALYSIS_RESULTS_DIR / "locality_cuisine_matrix.csv"
    assert matrix_file.exists()
    matrix_df = pd.read_csv(matrix_file)
    assert "location" in matrix_df.columns
    assert matrix_df.shape[0] == 10  # 10 localities
    assert matrix_df.shape[1] >= 10  # 10 cuisines + location column
