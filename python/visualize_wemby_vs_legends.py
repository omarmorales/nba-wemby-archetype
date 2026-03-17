import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# leer query
with open("sql/wemby_vs_legends.sql", "r") as file:
    query = file.read()

df = pd.read_sql(query, engine)

# 🧠 categorizar jugadores
def category(player):
    legends = [
        "Hakeem Olajuwon",
        "David Robinson",
        "Shaquille O'Neal",
        "Kareem Abdul-Jabbar"
    ]
    
    shooters = [
        "Dirk Nowitzki",
        "Kristaps Porzingis",
        "Karl-Anthony Towns"
    ]
    
    if player == "Victor Wembanyama":
        return "Wembanyama"
    elif player in legends:
        return "Legends"
    elif player in shooters:
        return "Stretch Bigs"
    else:
        return "Modern Bigs"

df["category"] = df["player"].apply(category)

# 🎨 gráfica
fig = px.scatter(
    df,
    x="height_m",
    y="avg_3p_pct",
    size="blk_per_game",
    color="category",

    hover_data={
        "player": True,
        "pts_per_game": True,
        "blk_per_game": True,
        "avg_3p_pct": True,
    },

    title="Wembanyama vs NBA Legends"
)

fig.write_html("visualizations/wemby_vs_legends.html")
fig.show()