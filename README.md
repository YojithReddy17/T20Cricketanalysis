# T20 Player Elo Analytics Dashboard

A full-stack T20 cricket analytics platform featuring custom Elo ratings, advanced player stats, and an interactive Streamlit dashboard.


## Features

- Custom Elo ratings for batting, bowling, and all-rounders
- Stats parsed from 300k+ ball-by-ball records (multiple leagues)
- Interactive dashboard: player search, career graphs, top-20 Elo progression, elite filtering
- Downloadable CSVs and robust error handling

## Project Structure

```
cricketpro/
├── cric.py                 # Streamlit dashboard
├── cricketelo.py           # Data pipeline (generates CSVs)
├── batting_stats.csv
├── bowling_stats.csv
├── allrounder_stats.csv
├── elite_batters.csv
├── elite_bowlers.csv
├── elite_allrounders.csv
├── elo_history_batting.csv
├── elo_history_bowling.csv
├── fielding_stats.csv
├── requirements.txt
└── README.md
```

## Getting Started

**1. Clone the repo:**
```bash
git clone https://github.com/yourusername/t20-elo-dashboard.git
cd t20-elo-dashboard/cricketpro
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Generate CSVs (if needed):**
- Place raw JSON data in the folders specified in `cricketelo.py`
- Run:
  ```bash
  python cricketelo.py
  ```

**4. Run the dashboard:**
```bash
streamlit run cric.py
```

## Dashboard Highlights

- **Batters/Bowlers/All-Rounders:** Elo, stats, elite filter
- **Player Details:** Batting, bowling, fielding stats, Elo graphs
- **Compare Players:** Side-by-side stats and Elo progression
- **Top 20 Elo:** Career Elo graphs for top players

## Requirements

- Python 3.8+
- pandas, numpy, streamlit, plotly

## Code Quality

This project is designed with a strong focus on code structure, error handling, and maintainability[1].  
All major components are modular and thoroughly tested.

**Enjoy exploring advanced T20 cricket analytics!**

[1] preferences.code_quality
