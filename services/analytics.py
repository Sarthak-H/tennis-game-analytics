"""
Analytics and Interactive Visualization Service.
Generates responsive Plotly charts using the modern sports analytics theme:
Deep Navy, Emerald Tennis Green, Crisp White, and Ice Silver.
"""

import pandas as pd
from typing import Optional

# Theme Color Palette
TENNIS_GREEN = "#00C853"
DARK_NAVY = "#0B192C"
NAVY_ACCENT = "#1E3E62"
SLATE_GRAY = "#4A5568"
LIGHT_BG = "#F8FAFC"
WHITE = "#FFFFFF"
CORAL_ACCENT = "#FF6B6B"
GOLD_ACCENT = "#FFD700"
SILVER_ACCENT = "#C0C0C0"
BRONZE_ACCENT = "#CD7F32"

THEME_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, Roboto, Segoe UI, sans-serif", "color": "#1E293B", "size": 12},
    "margin": {"l": 40, "r": 30, "t": 50, "b": 40},
    "hoverlabel": {"bgcolor": DARK_NAVY, "font_size": 13, "font_color": WHITE}
}


def create_competitors_by_country_chart(df: pd.DataFrame):
    """Horizontal bar chart of competitors by country."""
    import plotly.express as px
    if df.empty or "country" not in df.columns:
        return None

    top_countries = df.head(15).sort_values(by="competitor_count", ascending=True)

    fig = px.bar(
        top_countries,
        x="competitor_count",
        y="country",
        orientation="h",
        text="competitor_count",
        color="competitor_count",
        color_continuous_scale=[[0, "#2C5364"], [1, TENNIS_GREEN]],
        title="<b>Doubles Competitors by Country</b>"
    )
    fig.update_layout(
        **THEME_LAYOUT,
        xaxis_title="Number of Competitors",
        yaxis_title="",
        coloraxis_showscale=False
    )
    fig.update_traces(textposition="outside", marker_line_color=DARK_NAVY, marker_line_width=1)
    return fig


def create_competition_distribution_chart(df: pd.DataFrame):
    """Donut chart showing competition distribution by type."""
    import plotly.express as px
    if df.empty or "competition_type" not in df.columns:
        return None

    counts = df["competition_type"].fillna("Other").value_counts().reset_index()
    counts.columns = ["Type", "Count"]

    fig = px.pie(
        counts,
        names="Type",
        values="Count",
        hole=0.55,
        title="<b>Competitions by Format Type</b>",
        color_discrete_sequence=[TENNIS_GREEN, "#1E3E62", "#00B4D8", "#F77F00", "#D62828"]
    )
    fig.update_layout(**THEME_LAYOUT)
    fig.update_traces(textinfo="percent+label", pull=[0.05] * len(counts))
    return fig


def create_top_competitors_points_chart(df: pd.DataFrame, top_n: int = 10):
    """Bar chart of Top N Competitors by Points."""
    import plotly.express as px
    if df.empty or "points" not in df.columns:
        return None

    top_df = df.sort_values(by="points", ascending=True).tail(top_n)

    fig = px.bar(
        top_df,
        x="points",
        y="competitor_name",
        orientation="h",
        text="points",
        color="points",
        color_continuous_scale=[[0, "#1E3E62"], [1, TENNIS_GREEN]],
        title=f"<b>Top {top_n} Doubles Competitors by Ranking Points</b>"
    )
    fig.update_layout(
        **THEME_LAYOUT,
        xaxis_title="Ranking Points",
        yaxis_title="",
        coloraxis_showscale=False
    )
    fig.update_traces(texttemplate="%{x:,}", textposition="outside")
    return fig


def create_ranking_movement_chart(df: pd.DataFrame):
    """Movement distribution chart: Up, Stable, Down."""
    import plotly.graph_objects as go
    if df.empty or "movement" not in df.columns:
        return None

    gained = (df["movement"] > 0).sum()
    stable = (df["movement"] == 0).sum()
    dropped = (df["movement"] < 0).sum()

    categories = ["Rank Gained (▲)", "Stable (—)", "Rank Dropped (▼)"]
    values = [gained, stable, dropped]
    colors = [TENNIS_GREEN, "#64748B", CORAL_ACCENT]

    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            text=values,
            textposition="auto",
            marker=dict(color=colors, line=dict(color=DARK_NAVY, width=1))
        )
    ])
    fig.update_layout(
        **THEME_LAYOUT,
        title="<b>Weekly Ranking Movement Dynamics</b>",
        xaxis_title="",
        yaxis_title="Competitors Count"
    )
    return fig


def create_competitions_by_category_chart(df: pd.DataFrame):
    """Bar chart of competitions per category."""
    import plotly.express as px
    if df.empty or "category_name" not in df.columns:
        return None

    counts = df["category_name"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]

    fig = px.bar(
        counts,
        x="Category",
        y="Count",
        text="Count",
        color="Count",
        color_continuous_scale=[[0, "#2C5364"], [1, "#00C853"]],
        title="<b>Total Competitions per Category</b>"
    )
    fig.update_layout(
        **THEME_LAYOUT,
        xaxis_title="",
        yaxis_title="Total Competitions",
        coloraxis_showscale=False
    )
    fig.update_traces(textposition="outside")
    return fig


def create_venues_by_country_chart(df: pd.DataFrame):
    """Venues count grouped by country."""
    import plotly.express as px
    if df.empty or "country_name" not in df.columns:
        return None

    counts = df["country_name"].fillna("Unknown").value_counts().reset_index().head(12)
    counts.columns = ["Country", "Venues"]

    fig = px.bar(
        counts,
        x="Venues",
        y="Country",
        orientation="h",
        text="Venues",
        color="Venues",
        color_continuous_scale=[[0, "#1E3E62"], [1, TENNIS_GREEN]],
        title="<b>Venue Distribution Across Nations</b>"
    )
    fig.update_layout(
        **THEME_LAYOUT,
        xaxis_title="Venue Count",
        yaxis_title="",
        coloraxis_showscale=False
    )
    fig.update_traces(textposition="outside")
    return fig


def create_country_points_chart(df: pd.DataFrame, metric: str = "total_points"):
    """Chart displaying Country points (Total or Average)."""
    import plotly.express as px
    if df.empty or metric not in df.columns:
        return None

    metric_title = "Total Ranking Points" if metric == "total_points" else "Average Points per Competitor"
    sorted_df = df.sort_values(by=metric, ascending=False).head(15)

    fig = px.bar(
        sorted_df,
        x="country",
        y=metric,
        text=metric,
        color=metric,
        color_continuous_scale=[[0, "#0F2027"], [1, TENNIS_GREEN]],
        title=f"<b>{metric_title} by Country</b>"
    )
    fig.update_layout(
        **THEME_LAYOUT,
        xaxis_title="",
        yaxis_title=metric_title,
        coloraxis_showscale=False
    )
    fig.update_traces(texttemplate="%{y:,.0f}", textposition="outside")
    return fig

