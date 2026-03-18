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
radar_query   = open("sql/wemby_radar.sql").read()
bpm_query     = open("sql/wemby_bpm_rookies.sql").read()
unicorn_query = open("sql/wemby_unicorn.sql").read()
legends_query = open("sql/wemby_vs_legends.sql").read()

height_query = """
SELECT
  player,
  ht_in_in,
  (ht_in_in * 2.54 / 100) AS height_m
FROM players
WHERE ht_in_in IS NOT NULL;
"""

with engine.connect() as conn:
    df_scatter = pd.read_sql(scatter_query, conn)
    df_radar   = pd.read_sql(radar_query,   conn)
    df_height  = pd.read_sql(height_query,  conn)
    df_bpm     = pd.read_sql(bpm_query,     conn)
    df_unicorn = pd.read_sql(unicorn_query, conn)
    df_legends = pd.read_sql(legends_query, conn)

# =========================
# DEBUG
# =========================
print("Scatter rows: ", len(df_scatter))
print("BPM rows:     ", len(df_bpm))
print("Unicorn rows: ", len(df_unicorn))
print("Legends rows: ", len(df_legends))
print(df_legends[["player", "bpm", "pts_per_game", "blk_per_game"]])

# =========================
# NORMALIZE RADAR
# =========================
def normalize(series):
    return 100 * (series - series.min()) / (series.max() - series.min())

df_radar["score_pts"]    = normalize(df_radar["pts_per_game"])
df_radar["score_3p"]     = normalize(df_radar["avg_3p_pct"])
df_radar["score_blk"]    = normalize(df_radar["blk_per_game"])
df_radar["score_height"] = normalize(df_radar["ht_in_in"])

# =========================
# LAYOUT 4 rows x 2 cols
# =========================
fig = make_subplots(
    rows=4, cols=2,
    specs=[
        [{"type": "scatter"},   {"type": "polar"}],
        [{"type": "histogram"}, {"type": "domain"}],
        [{"type": "bar"},       {"type": "domain"}],
        [{"type": "scatter"},   {"type": "bar"}]
    ],
    subplot_titles=(
        "Archetype Scatter",          "Player Radar",
        "NBA Height Distribution",    "Insights",
        "Best Rookie BPM Seasons Ever", "",
        "The Unicorn Zone",           "Year 1 vs Legends"
    ),
    horizontal_spacing=0.15,
    vertical_spacing=0.10
)

# =========================
# ROW 1 LEFT — SCATTER
# =========================
marker_sizes = (df_scatter["blk_per_game"] * 10).clip(lower=6)
colors = ["red" if p == "Victor Wembanyama" else "steelblue"
          for p in df_scatter["player"]]

fig.add_trace(
    go.Scatter(
        x=df_scatter["height_m"],
        y=df_scatter["avg_3p_pct"],
        mode="markers",
        marker=dict(
            size=marker_sizes,
            color=colors,
            opacity=0.7,
            line=dict(width=0.5, color="white")
        ),
        text=df_scatter["player"],
        hovertemplate="<b>%{text}</b><br>Height: %{x:.2f}m<br>3P%: %{y:.1%}<extra></extra>",
        name="Players"
    ),
    row=1, col=1
)

# =========================
# ROW 1 RIGHT — RADAR
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
        name="Wembanyama",
        line=dict(color="red"),
        fillcolor="rgba(255,0,0,0.2)"
    ),
    row=1, col=2
)

# =========================
# ROW 2 LEFT — HISTOGRAM
# =========================
fig.add_trace(
    go.Histogram(
        x=df_height["height_m"],
        name="All Players",
        marker_color="steelblue",
        opacity=0.8
    ),
    row=2, col=1
)

# detect histogram axis at runtime
histogram_trace = None
for trace in fig.data:
    if isinstance(trace, go.Histogram):
        histogram_trace = trace
        break

xaxis_key = getattr(histogram_trace, "xaxis", "x") or "x"
yaxis_key = getattr(histogram_trace, "yaxis", "y") or "y"

print("Histogram xaxis:", xaxis_key)
print("Histogram yaxis:", yaxis_key)

fig.add_shape(
    type="line",
    x0=2.24, x1=2.24,
    y0=0, y1=1,
    yref=yaxis_key + " domain",
    xref=xaxis_key,
    line=dict(color="red", width=2, dash="dash")
)

fig.add_annotation(
    x=2.24,
    y=0.58,
    xref=xaxis_key,
    yref="paper",
    text="Wembanyama<br>2.24m",
    showarrow=True,
    arrowhead=2,
    arrowcolor="red",
    ax=30,
    ay=-30,
    font=dict(color="red", size=11),
    bgcolor="white",
    bordercolor="red"
)

# =========================
# ROW 2 RIGHT — INSIGHTS TEXT
# =========================
fig.add_annotation(
    text=(
        "<b>Wembanyama Archetype</b><br><br>"
        "Extreme height (clear outlier)<br>"
        "Above-average 3PT shooting<br>"
        "Elite rim protection<br><br>"
        "<b>Conclusion:</b><br>"
        "Unique player profile in NBA history"
    ),
    x=0.78, y=0.72,
    xref="paper", yref="paper",
    showarrow=False,
    align="left",
    font=dict(size=13)
)

# =========================
# ROW 3 LEFT — BPM ROOKIE BAR CHART
# =========================
df_bpm_sorted = df_bpm.sort_values("bpm", ascending=True)

bar_colors_bpm = [
    "red" if "Wembanyama" in p else "steelblue"
    for p in df_bpm_sorted["player"]
]

bpm_labels = [
    f"{row['player']} ({int(row['rookie_season'])})"
    for _, row in df_bpm_sorted.iterrows()
]

fig.add_trace(
    go.Bar(
        x=df_bpm_sorted["bpm"],
        y=bpm_labels,
        orientation="h",
        marker=dict(color=bar_colors_bpm, line=dict(width=0.5, color="white")),
        text=df_bpm_sorted["bpm"].round(1),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>BPM: %{x:.1f}<extra></extra>",
        name="Rookie BPM"
    ),
    row=3, col=1
)

# detect BPM bar axis at runtime — avoids add_vline polar conflict
bpm_bar_trace = None
for trace in fig.data:
    if isinstance(trace, go.Bar) and getattr(trace, "orientation", None) == "h":
        bpm_bar_trace = trace
        break

bpm_xaxis = getattr(bpm_bar_trace, "xaxis", "x3") or "x3"
bpm_yaxis = getattr(bpm_bar_trace, "yaxis", "y3") or "y3"

fig.add_shape(
    type="line",
    x0=0, x1=0,
    y0=0, y1=1,
    xref=bpm_xaxis,
    yref=bpm_yaxis + " domain",
    line=dict(color="gray", width=1)
)

# =========================
# ROW 4 LEFT — UNICORN ZONE SCATTER
# =========================
is_wemby   = df_unicorn["player"] == "Victor Wembanyama"
is_notable = (df_unicorn["blk_per_game"] >= 2.0) & ~is_wemby
df_rest    = df_unicorn[~is_wemby & ~is_notable]
df_notable = df_unicorn[is_notable]
df_wemby   = df_unicorn[is_wemby]

# debug — print wemby row to confirm data exists
print("Wemby in unicorn data:", len(df_wemby), "rows")
if len(df_wemby) > 0:
    print(df_wemby[["player", "pts_per_game", "blk_per_game"]])
else:
    print("WARNING: Wemby not found — may have fewer than 200 career games in data")
    print("Top unicorn rows:")
    print(df_unicorn.sort_values("blk_per_game", ascending=False).head(10))

# regular players
fig.add_trace(
    go.Scatter(
        x=df_rest["pts_per_game"],
        y=df_rest["blk_per_game"],
        mode="markers",
        marker=dict(size=5, color="steelblue", opacity=0.5,
                    line=dict(width=0.3, color="white")),
        text=df_rest["player"],
        hovertemplate="<b>%{text}</b><br>PPG: %{x:.1f}<br>BPG: %{y:.2f}<extra></extra>",
        name="Other Players"
    ),
    row=4, col=1
)

# elite blockers / scorers (orange)
fig.add_trace(
    go.Scatter(
        x=df_notable["pts_per_game"],
        y=df_notable["blk_per_game"],
        mode="markers",
        marker=dict(size=9, color="orange", opacity=0.75,
                    line=dict(width=0.5, color="white")),
        text=df_notable["player"],
        hovertemplate="<b>%{text}</b><br>PPG: %{x:.1f}<br>BPG: %{y:.2f}<extra></extra>",
        name="Elite Blockers"
    ),
    row=4, col=1
)

# Wemby — separate trace, bright red star, always visible
if len(df_wemby) > 0:
    fig.add_trace(
        go.Scatter(
            x=df_wemby["pts_per_game"],
            y=df_wemby["blk_per_game"],
            mode="markers+text",
            marker=dict(
                size=22,
                color="red",
                symbol="star",
                line=dict(width=1.5, color="darkred")
            ),
            text=["Wembanyama"],
            textposition="top center",
            textfont=dict(color="red", size=12),
            hovertemplate="<b>Wembanyama</b><br>PPG: %{x:.1f}<br>BPG: %{y:.2f}<extra></extra>",
            name="Wembanyama"
        ),
        row=4, col=1
    )

# =========================
# ROW 4 RIGHT — YEAR 1 VS LEGENDS
# =========================
metrics  = ["bpm", "pts_per_game", "blk_per_game"]
labels_m = ["BPM", "PPG", "BPG"]
colors_m = ["#636EFA", "#00CC96", "#EF553B"]

for metric, label, color in zip(metrics, labels_m, colors_m):
    bar_colors_l = [
        "red" if p == "Victor Wembanyama" else color
        for p in df_legends["player"]
    ]
    fig.add_trace(
        go.Bar(
            name=label,
            x=df_legends["player"],
            y=df_legends[metric],
            marker_color=bar_colors_l,
            opacity=0.85,
            text=df_legends[metric].round(1),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>" + label + ": %{y:.1f}<extra></extra>"
        ),
        row=4, col=2
    )

fig.update_layout(barmode="group")

# =========================
# RADAR TITLE nudge
# =========================
fig.layout.annotations[1].update(
    y=fig.layout.annotations[1].y + 0.02
)

# =========================
# AXES LABELS
# =========================
fig.update_xaxes(title_text="Height (m)",            row=1, col=1)
fig.update_yaxes(title_text="3P%",                   row=1, col=1)
fig.update_xaxes(title_text="Height (m)",            row=2, col=1)
fig.update_yaxes(title_text="# Players",             row=2, col=1)
fig.update_xaxes(title_text="Box Plus/Minus (BPM)",  row=3, col=1)
fig.update_xaxes(title_text="Points Per Game",       row=4, col=1)
fig.update_yaxes(title_text="Blocks Per Game",       row=4, col=1)
fig.update_yaxes(title_text="Value",                 row=4, col=2)
fig.update_xaxes(tickangle=-30,                      row=4, col=2)

# =========================
# FINAL LAYOUT
# =========================
fig.update_layout(
    title=dict(
        text="NBA Wembanyama Analysis Dashboard",
        font=dict(size=22)
    ),
    height=1600,
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.01,
        xanchor="right",
        x=1
    ),
    plot_bgcolor="white",
    paper_bgcolor="white"
)

fig.write_html("visualizations/wemby_dashboard.html")
fig.show()