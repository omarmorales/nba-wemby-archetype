import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# =========================
# LOAD DATA
# =========================
scatter_query = open("sql/wemby_archetype.sql").read()
radar_query = open("sql/wemby_radar.sql").read()

df_scatter = pd.read_sql(scatter_query, engine)
df_radar = pd.read_sql(radar_query, engine)

# =========================
# NORMALIZE RADAR
# =========================
def normalize(series):
    return 100 * (series - series.min()) / (series.max() - series.min())

df_radar["score_pts"] = normalize(df_radar["pts_per_game"])
df_radar["score_3p"] = normalize(df_radar["avg_3p_pct"])
df_radar["score_blk"] = normalize(df_radar["blk_per_game"])
df_radar["score_height"] = normalize(df_radar["ht_in_in"])

# =========================
# CREATE LAYOUT
# =========================
fig = make_subplots(
    rows=2, cols=2,
    specs=[
        [{"type": "scatter"}, {"type": "polar"}],
        [{"type": "histogram"}, {"type": "domain"}]
    ],
    subplot_titles=(
        "Archetype Scatter",
        "Player Radar",
        "Height Distribution",
        "Insights"
    )
)

# =========================
# SCATTER
# =========================
fig.add_trace(
    go.Scatter(
        x=df_scatter["height_m"],
        y=df_scatter["avg_3p_pct"],
        mode="markers",
        marker=dict(
            size=df_scatter["blk_per_game"] * 10,
            color="blue"
        ),
        text=df_scatter["player"],
        name="Players"
    ),
    row=1, col=1
)

# =========================
# RADAR (solo Wemby)
# =========================
wemby = df_radar[df_radar["player"] == "Victor Wembanyama"].iloc[0]

categories = ["Scoring", "Shooting", "Defense", "Height"]

values = [
    wemby["score_pts"],
    wemby["score_3p"],
    wemby["score_blk"],
    wemby["score_height"]
]
values += values[:1]

fig.add_trace(
    go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill="toself",
        name="Wemby"
    ),
    row=1, col=2
)

# =========================
# HISTOGRAM
# =========================
fig.add_trace(
    go.Histogram(
        x=df_scatter["height_m"],
        name="Height Distribution"
    ),
    row=2, col=1
)

# =========================
# TEXT INSIGHTS
# =========================
fig.add_annotation(
    text=(
        "<b>Wembanyama Archetype</b><br><br>"
        "• Elite height + shooting + defense<br>"
        "• Rare combination historically<br>"
        "• Represents evolution of NBA big men"
    ),
    x=0.75, y=0.2,
    xref="paper", yref="paper",
    showarrow=False,
    align="left",
    font=dict(size=14)
)

# =========================
# FINAL TOUCH
# =========================
fig.update_layout(
    title="NBA Wembanyama Analysis Dashboard",
    height=800,
    showlegend=False
)

fig.write_html("visualizations/wemby_dashboard.html")
fig.show()