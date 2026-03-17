import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# conexión
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# 🔥 leer SQL desde archivo
with open("sql/wemby_archetype.sql", "r") as file:
    query = file.read()

df = pd.read_sql(query, engine)
df = df.dropna()

# 🎯 identificar jugadores
wemby_name = "Victor Wembanyama"
top_n = 5

top_players = df[df["player"] != wemby_name].head(top_n)["player"].tolist()

# tamaños
sizes = df["blk_per_game"] * 120

# colores
colors = []
for player in df["player"]:
    if player == wemby_name:
        colors.append("orange")
    elif player in top_players:
        colors.append("green")
    else:
        colors.append("gray")

# gráfico
plt.figure()

plt.scatter(
    df["height_m"],
    df["avg_3p_pct"],
    s=sizes,
    c=colors,
    alpha=0.7
)

# etiquetas
for _, row in df.iterrows():
    if row["player"] == wemby_name or row["player"] in top_players:
        plt.text(
            row["height_m"] + 0.002,
            row["avg_3p_pct"],
            row["player"],
            fontsize=8
        )

plt.xlabel("Height (meters)")
plt.ylabel("3P%")
plt.title("How Unique is Victor Wembanyama?")

plt.savefig("visualizations/wemby_scatter_pro.png")
plt.show()