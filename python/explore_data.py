import pandas as pd

players = pd.read_csv("data/raw/Player Career Info.csv")
totals = pd.read_csv("data/raw/Player Totals.csv")

print(players.head())
print(players.info())

print(totals.head())
print(totals.info())
