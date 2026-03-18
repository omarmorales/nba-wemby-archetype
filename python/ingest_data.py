import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("Host:", DB_HOST)
print("User:", DB_USER)
print("Port:", DB_PORT)
print("DB:  ", DB_NAME)

# =========================
# LOAD CSVs
# =========================
players  = pd.read_csv("data/raw/Player Career Info.csv")
totals   = pd.read_csv("data/raw/Player Totals.csv")
advanced = pd.read_csv("data/raw/Advanced.csv")
shooting = pd.read_csv("data/raw/Player Shooting.csv")

# =========================
# CLEAN COLUMN NAMES
# =========================
for df in [players, totals, advanced, shooting]:
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("%", "_pct")
        .str.replace("/", "_per_")
        .str.replace("+", "plus")
        .str.replace("-", "minus")
    )

# =========================
# CLEAN PLAYERS
# =========================
players["birth_date"] = pd.to_datetime(players["birth_date"], errors="coerce")
players["debut"]      = pd.to_datetime(players["debut"],      errors="coerce")
players = players.drop_duplicates(subset="player_id")

# =========================
# CLEAN TOTALS
# remove duplicate rows that appear in some Kaggle versions
# (same player_id + season but different team = traded players)
# keep "TOT" row which is the season total
# =========================
if "tm" in totals.columns:
    totals_tot   = totals[totals["tm"] == "TOT"]
    totals_other = totals[~totals["player_id"].isin(totals_tot["player_id"])]
    totals = pd.concat([totals_tot, totals_other], ignore_index=True)

# =========================
# CLEAN ADVANCED
# same traded-player dedup logic
# =========================
if "tm" in advanced.columns:
    adv_tot   = advanced[advanced["tm"] == "TOT"]
    adv_other = advanced[~advanced["player_id"].isin(adv_tot["player_id"])]
    advanced  = pd.concat([adv_tot, adv_other], ignore_index=True)

# drop duplicate unnamed columns that sometimes appear in advanced.csv
advanced = advanced.loc[:, ~advanced.columns.str.startswith("unnamed")]

# =========================
# CONNECTION
# =========================
engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# =========================
# INGEST
# =========================
with engine.connect() as conn:
    players.to_sql("players",  conn, if_exists="replace", index=False)
    print("players  loaded:", len(players),  "rows")

    totals.to_sql("totals",    conn, if_exists="replace", index=False)
    print("totals   loaded:", len(totals),   "rows")

    advanced.to_sql("advanced", conn, if_exists="replace", index=False)
    print("advanced loaded:", len(advanced), "rows")

    shooting.to_sql("shooting", conn, if_exists="replace", index=False)
    print("shooting loaded:", len(shooting), "rows")

print("\nAll data ingested successfully!")