# 🏀 The Wembanyama Archetype

This project explores how unique Victor Wembanyama is compared to other NBA players using data analysis, SQL modeling, and interactive visualizations.

---

## 📊 Objective

Identify players who match the "Wembanyama archetype":

* Elite height (7ft+)
* 3-point shooting ability
* Rim protection (blocks)

---

## 🧠 Key Insight

While several players match one or two of these traits, very few match all three at a high level.

This suggests that Wembanyama represents a **rare and emerging player archetype in modern basketball**.

---

## 🛠️ Tech Stack

* Python (Pandas, SQLAlchemy)
* PostgreSQL (Supabase)
* SQL (CTEs, window functions)
* Plotly for interactive visualization
* Matplotlib

---

## 🏗️ Project Structure

```
nba-wemby-prototype/

data/
  raw/

python/
  explore_data.py
  ingest_data.py
  visualize.py
  visualize_plotly.py

sql/
  player_stats.sql
  ranked_players.sql
  wemby_archetype.sql

visualizations/
  wemby_scatter.png
  wemby_interactive.html

insights/
  wemby_analysis.md
```

---

## ⚙️ Data Pipeline

1. Download NBA data from Kaggle
2. Clean and explore using Python
3. Load data into PostgreSQL (Supabase)
4. Transform data using SQL:

   * Aggregations
   * Feature engineering (Wemby score)
   * Ranking players
5. Visualize results with Python

---

## 📈 Visualization

The interactive chart highlights:

* Height (meters)
* 3-point shooting %
* Blocks per game (bubble size)
* Top comparable players

---

## 🚀 How to Run

```bash
python python/ingest_data.py
python python/visualize_plotly.py
```

---

## 💡 Future Improvements

* Build a Next.js dashboard
* Add filters (season, team, position)
* Deploy as a public web app
* Add API layer for querying player data

---

## 👨‍💻 Author

Omar Morales
Web UI Developer | Data Enthusiast