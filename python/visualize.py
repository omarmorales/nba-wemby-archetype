import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# conexión
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

query = """
WITH player_stats AS (
  SELECT
    p.player,
    p.ht_in_in,

    AVG(t.x3p_percent) AS avg_3p_pct,
    SUM(t.blk) / SUM(t.g) AS blk_per_game,
    SUM(t.x3pa) AS total_3pa,
    SUM(t.g) AS total_games

  FROM players p
  JOIN totals t 
    ON p.player_id = t.player_id

  WHERE 
    p.ht_in_in IS NOT NULL
    AND t.season >= 2010

  GROUP BY p.player, p.ht_in_in

  HAVING 
    SUM(t.x3pa) > 100
    AND SUM(t.g) > 100
    AND (SUM(t.blk) / SUM(t.g)) >= 1.0
),

ranked AS (
  SELECT
    player,
    ht_in_in,
    avg_3p_pct,
    blk_per_game,

    PERCENT_RANK() OVER (ORDER BY ht_in_in) AS height_score,
    PERCENT_RANK() OVER (ORDER BY avg_3p_pct) AS shooting_score,
    PERCENT_RANK() OVER (ORDER BY blk_per_game) AS defense_score

  FROM player_stats
),

final AS (
  SELECT
    player,
    ht_in_in,
    (ht_in_in * 2.54 / 100) AS height_m,
    avg_3p_pct,
    blk_per_game,

    (
      height_score * 0.4 +
      shooting_score * 0.25 +
      defense_score * 0.35
    ) AS wemby_score

  FROM ranked
)

SELECT *
FROM final
WHERE ht_in_in >= 84
ORDER BY wemby_score DESC;
"""

df = pd.read_sql(query, engine)
df = df.dropna()

# 🎯 identificar jugadores
wemby_name = "Victor Wembanyama"
top_n = 5

top_players = df[df["player"] != wemby_name].head(top_n)["player"].tolist()

# 🎨 categoría para colores
def categorize(player):
    if player == wemby_name:
        return "Wembanyama"
    elif player in top_players:
        return "Top Comparables"
    else:
        return "Others"

df["category"] = df["player"].apply(categorize)

# 🚀 gráfico interactivo
fig = px.scatter(
    df,
    x="height_m",
    y="avg_3p_pct",
    size="blk_per_game",
    color="category",

    hover_data={
        "player": True,
        "height_m": ":.2f",
        "avg_3p_pct": ":.3f",
        "blk_per_game": ":.2f",
        "wemby_score": ":.3f",
    },

    title="How Unique is Victor Wembanyama?",
)

# 🔥 mejorar layout
fig.update_traces(marker=dict(opacity=0.75))

fig.update_layout(
    xaxis_title="Height (meters)",
    yaxis_title="3P%",
    legend_title="Category"
)

# 💾 guardar html interactivo
fig.write_html("visualizations/wemby_interactive.html")

fig.show()