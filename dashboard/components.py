"""
Dashboard UI Components Module
Reusable presentation components for Streamlit analytics dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_header():
    """Renders project title banner."""
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                    padding: 24px; border-radius: 12px; color: white; margin-bottom: 24px;">
            <h1 style="color: white; margin-bottom: 6px; font-size: 28px;">
                🍽️ Zomato Bangalore Restaurant Analytics
            </h1>
            <p style="font-size: 15px; margin-bottom: 0px; opacity: 0.95;">
                Enterprise Big Data Analytics & Interactive Intelligence Platform
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metrics_cards(
    total_count: int,
    avg_rating: float,
    total_votes: int,
    avg_cost: float,
    num_localities: int,
    is_filtered: bool = False
):
    """Renders summary KPI cards."""
    status_label = " (Filtered)" if is_filtered else " (Overall)"
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            label=f"Restaurants{status_label}",
            value=f"{total_count:,}"
        )
    with c2:
        st.metric(
            label=f"Avg Rating{status_label}",
            value=f"{avg_rating:.2f} / 5.0" if avg_rating else "N/A"
        )
    with c3:
        st.metric(
            label=f"Total Votes{status_label}",
            value=f"{total_votes:,}"
        )
    with c4:
        st.metric(
            label=f"Avg Cost for Two{status_label}",
            value=f"₹{avg_cost:.0f}" if avg_cost else "N/A"
        )
    with c5:
        st.metric(
            label=f"Localities{status_label}",
            value=f"{num_localities}"
        )


def render_locality_chart(locality_df: pd.DataFrame):
    """Renders interactive horizontal bar chart for top localities."""
    top_10 = locality_df.head(10).sort_values("restaurant_count", ascending=True)
    fig = px.bar(
        top_10,
        x="restaurant_count",
        y="location",
        orientation="h",
        text="restaurant_count",
        title="Top 10 Localities by Restaurant Concentration",
        labels={"restaurant_count": "Restaurant Count", "location": "Bangalore Locality"},
        color="avg_rating",
        color_continuous_scale="Reds",
        hover_data=["avg_rating", "total_votes", "avg_approx_cost"]
    )
    fig.update_layout(template="plotly_white", height=420, margin=dict(l=10, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)


def render_cuisine_matrix_chart(matrix_df: pd.DataFrame):
    """Renders advanced interactive heatmap for Locality vs Cuisine."""
    fig = px.imshow(
        matrix_df,
        labels=dict(x="Cuisine Category", y="Locality", color="Count"),
        x=matrix_df.columns,
        y=matrix_df.index,
        color_continuous_scale="YlOrRd",
        text_auto=True,
        title="Advanced Locality vs. Cuisine Concentration Heatmap"
    )
    fig.update_layout(
        template="plotly_white",
        height=480,
        xaxis_tickangle=-45,
        margin=dict(l=20, r=20, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)


def render_cost_rating_scatter(df: pd.DataFrame):
    """Renders interactive Cost vs Rating bubble chart."""
    sample = df.dropna(subset=["rating_num", "approx_cost_num"]).sample(min(800, len(df)), random_state=42)
    fig = px.scatter(
        sample,
        x="approx_cost_num",
        y="rating_num",
        size="votes_num",
        color="online_order",
        hover_name="name",
        hover_data=["location", "cuisines"],
        title="Approximate Cost vs. Customer Rating (Bubble Size = Total Votes)",
        labels={
            "approx_cost_num": "Cost for Two (₹)",
            "rating_num": "Rating (out of 5)",
            "online_order": "Online Ordering"
        },
        color_discrete_map={"Yes": "#10b981", "No": "#ef4444"}
    )
    fig.update_layout(template="plotly_white", height=430)
    st.plotly_chart(fig, use_container_width=True)


def render_rating_distribution_chart(df: pd.DataFrame):
    """Renders rating distribution histogram."""
    rated = df.dropna(subset=["rating_num"])
    fig = px.histogram(
        rated,
        x="rating_num",
        nbins=25,
        title="Empirical Customer Rating Distribution",
        labels={"rating_num": "Rating (out of 5.0)"},
        color_discrete_sequence=["#3b82f6"]
    )
    fig.update_layout(template="plotly_white", height=380, bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)
