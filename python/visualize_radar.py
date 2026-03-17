import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# cargar data
with open("sql/wemby_radar.sql", "r") as file:
    query = file.read()

df = pd.read_sql(query, engine)

# 🔥 NORMALIZAR (0–100)
def normalize(series):
    return 100 * (series - series.min()) / (series.max() - series.min())

df["score_pts"] = normalize(df["pts_per_game"])
df["score_3p"] = normalize(df["avg_3p_pct"])
df["score_blk"] = normalize(df["blk_per_game"])
df["score_height"] = normalize(df["ht_in_in"])

# categorías radar
categories = ["Scoring", "Shooting", "Defense", "Height"]

fig = go.Figure()

for _, row in df.iterrows():
    values = [
        row["score_pts"],
        row["score_3p"],
        row["score_blk"],
        row["score_height"]
    ]
    
    # cerrar el círculo
    values += values[:1]

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        name=row["player"]
    ))

fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100])
    ),
    title="Wembanyama vs NBA Players (2K Style Radar)"
)

fig.write_html("visualizations/wemby_radar.html")
fig.show()