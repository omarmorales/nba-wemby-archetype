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

print(DB_HOST)
print(DB_USER)
print(DB_PORT)
print(DB_NAME)

# load data
players = pd.read_csv("data/raw/Player Career Info.csv")
totals = pd.read_csv("data/raw/Player Totals.csv")

# Clean column's names
players.columns = players.columns.str.lower()
totals.columns = totals.columns.str.lower()

# convert dates
players["birth_date"] = pd.to_datetime(players["birth_date"], errors="coerce")
players["debut"] = pd.to_datetime(players["debut"], errors="coerce")

# Eliminate duplicates
players = players.drop_duplicates(subset="player_id")

# Conection to postgreSQL
engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# load tables
players.to_sql("players", engine, if_exists="replace", index=False)
totals.to_sql("totals", engine, if_exists="replace", index=False)

print("Data has been ingested successfully!")