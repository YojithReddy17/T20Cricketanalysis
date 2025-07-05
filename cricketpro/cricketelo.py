import os
import json
import pandas as pd
import numpy as np

# --- Step 1: Set up your folders (adjust as needed, use forward slashes for Windows) ---
league_folders = [
    ('C:/Users/Yojit/Downloads/ipl_male_json', 'IPL'),
    ('C:/Users/Yojit/Downloads/bbl_male_json', 'BBL'),
    ('C:/Users/Yojit/Downloads/psl_male_json', 'PSL'),
    ('C:/Users/Yojit/Downloads/cpl_male_json', 'CPL'),
    ('C:/Users/Yojit/Downloads/icc_mens_t20_world_cup_male_json', 'T20WC'),
    ('C:/Users/Yojit/Downloads/sma_male_json', 'SMAT'),
    ('C:/Users/Yojit/Downloads/sat_male_json', 'SAT'),
    ('C:/Users/Yojit/Downloads/t20i_male_json', 'T20I')
]

def extract_fielder_names(fielders):
    # Handles list of dicts (with "name") or list of strings
    names = []
    if isinstance(fielders, list):
        for f in fielders:
            if isinstance(f, dict) and "name" in f:
                names.append(f["name"])
            elif isinstance(f, str):
                names.append(f)
    elif isinstance(fielders, dict) and "name" in fielders:
        names.append(fielders["name"])
    return names

bat_rows, bowl_rows, fielding_rows = [], [], []

for folder, league in league_folders:
    if os.path.exists(folder):
        for fname in os.listdir(folder):
            if fname.endswith('.json'):
                file_path = os.path.join(folder, fname)
                with open(file_path, 'r') as f:
                    match = json.load(f)
                info = match.get('info', {})
                date = info.get('dates', [''])[0] if isinstance(info.get('dates', []), list) else info.get('dates', '')
                match_type = info.get('match_type', 'T20')
                innings = match.get('innings', [])
                for inning in innings:
                    team = inning.get('team', '')
                    overs = inning.get('overs', [])
                    for over in overs:
                        for delivery in over.get('deliveries', []):
                            # Batting
                            batter = delivery.get('batter', '')
                            runs = delivery.get('runs', {}).get('batter', 0)
                            bat_rows.append({
                                'player': batter,
                                'team': team,
                                'league': league,
                                'date': date,
                                'runs': runs,
                                'balls': 1,
                                'match_type': match_type
                            })
                            # Bowling
                            bowler = delivery.get('bowler', '')
                            runs_conceded = delivery.get('runs', {}).get('total', 0)
                            wicket = 1 if 'wickets' in delivery else 0
                            bowl_rows.append({
                                'player': bowler,
                                'team': team,
                                'league': league,
                                'date': date,
                                'runs_conceded': runs_conceded,
                                'balls': 1,
                                'wickets': wicket,
                                'match_type': match_type
                            })
                            # Fielding
                            if 'wickets' in delivery:
                                for wicket_info in delivery['wickets']:
                                    kind = wicket_info.get('kind', '')
                                    fielders = wicket_info.get('fielders', [])
                                    fielder_names = extract_fielder_names(fielders)
                                    if kind == 'caught':
                                        for fielder_name in fielder_names:
                                            if fielder_name:
                                                fielding_rows.append({
                                                    'player': fielder_name,
                                                    'event': 'catch',
                                                    'date': date,
                                                    'league': league
                                                })
                                    elif kind == 'run out':
                                        for fielder_name in fielder_names:
                                            if fielder_name:
                                                fielding_rows.append({
                                                    'player': fielder_name,
                                                    'event': 'run_out',
                                                    'date': date,
                                                    'league': league
                                                })
                                    elif kind == 'stumped':
                                        for fielder_name in fielder_names:
                                            if fielder_name:
                                                fielding_rows.append({
                                                    'player': fielder_name,
                                                    'event': 'stumping',
                                                    'date': date,
                                                    'league': league
                                                })

# --- Batting aggregation ---
bat_df = pd.DataFrame(bat_rows)
bat_df['date'] = pd.to_datetime(bat_df['date'], errors='coerce')
bat_df['match_id'] = bat_df['date'].astype(str) + "_" + bat_df['league'] + "_" + bat_df['team']
agg_bat = bat_df.groupby(['player', 'match_id']).agg(
    runs=('runs', 'sum'),
    balls=('balls', 'sum'),
    league=('league', 'first'),
    match_type=('match_type', 'first'),
    date=('date', 'first')
).reset_index()
career_bat = agg_bat.groupby('player').agg(
    total_runs=('runs', 'sum'),
    total_balls=('balls', 'sum'),
    matches_played=('match_id', 'nunique')
)
career_bat['bat_avg'] = career_bat['total_runs'] / career_bat['matches_played']
career_bat['strike_rate'] = (career_bat['total_runs'] / career_bat['total_balls']) * 100
career_bat['milestone_1000_runs'] = career_bat['total_runs'] >= 1000

# --- Batting Elo ---
K_base = 10
elo_batting = {player: 1500 for player in career_bat.index}
elo_history = []
for idx, row in agg_bat.iterrows():
    batter = row['player']
    runs = row['runs']
    K = K_base
    batter_result = np.log1p(runs) / np.log1p(30)
    if runs >= 150:
        batter_result += 0.15
    elif runs >= 50:
        batter_result += 0.05
    batter_result = min(batter_result, 1.0)
    old_bat_elo = elo_batting.get(batter, 1500)
    expected_bat = 0.5
    elo_batting[batter] = old_bat_elo + K * (batter_result - expected_bat)
    elo_history.append({
        'date': row['date'],
        'batter': batter,
        'batting_elo': elo_batting[batter],
        'league': row['league']
    })
elo_df = pd.DataFrame(elo_history)
elo_df['date'] = pd.to_datetime(elo_df['date'], errors='coerce')
final_batting_elo = elo_df.groupby('batter')['batting_elo'].last()
career_bat['batting_elo'] = final_batting_elo

career_bat.to_csv('batting_stats.csv')
elo_df.to_csv('elo_history_batting.csv', index=False)

# --- Bowling aggregation ---
bowl_df = pd.DataFrame(bowl_rows)
bowl_df['date'] = pd.to_datetime(bowl_df['date'], errors='coerce')
bowl_df['match_id'] = bowl_df['date'].astype(str) + "_" + bowl_df['league'] + "_" + bowl_df['team']
agg_bowl = bowl_df.groupby(['player', 'match_id']).agg(
    wickets=('wickets', 'sum'),
    balls=('balls', 'sum'),
    runs_conceded=('runs_conceded', 'sum'),
    league=('league', 'first'),
    match_type=('match_type', 'first'),
    date=('date', 'first')
).reset_index()
agg_bowl = agg_bowl[agg_bowl['balls'] >= 12]
career_bowl = agg_bowl.groupby('player').agg(
    matches_2plus_overs=('match_id', 'nunique'),
    total_wickets=('wickets', 'sum'),
    total_balls=('balls', 'sum'),
    total_runs=('runs_conceded', 'sum')
)
career_bowl['bowling_avg'] = career_bowl['total_runs'] / career_bowl['total_wickets'].replace(0, np.nan)
career_bowl['economy'] = career_bowl['total_runs'] / (career_bowl['total_balls'] / 6).replace(0, np.nan)
career_bowl['wickets_per_match'] = career_bowl['total_wickets'] / career_bowl['matches_2plus_overs']
career_bowl['milestone_100_wickets'] = career_bowl['total_wickets'] >= 100

# --- Bowling Elo ---
K_base = 10
elo_bowling = {player: 1500 for player in career_bowl.index}
elo_bowl_history = []
for idx, row in agg_bowl.iterrows():
    bowler = row['player']
    wickets = row['wickets']
    balls = row['balls']
    runs = row['runs_conceded']
    K = K_base
    economy = (runs / (balls / 6)) if balls > 0 else 8
    result = (wickets / 2) - ((economy - 7.5) / 7.5) * 0.25
    result = max(0, min(1, result))
    old_elo = elo_bowling.get(bowler, 1500)
    expected = 0.5
    elo_bowling[bowler] = old_elo + K * (result - expected)
    elo_bowl_history.append({
        'date': row['date'],
        'bowler': bowler,
        'bowling_elo': elo_bowling[bowler],
        'league': row['league']
    })
elo_bowl_df = pd.DataFrame(elo_bowl_history)
elo_bowl_df['date'] = pd.to_datetime(elo_bowl_df['date'], errors='coerce')
final_bowling_elo = elo_bowl_df.groupby('bowler')['bowling_elo'].last()
career_bowl['bowling_elo'] = final_bowling_elo

career_bowl.to_csv('bowling_stats.csv')
elo_bowl_df.to_csv('elo_history_bowling.csv', index=False)

# --- All-rounders ---
allrounder_df = career_bat[['batting_elo', 'total_runs', 'matches_played']].merge(
    career_bowl[['bowling_elo', 'total_wickets', 'matches_2plus_overs']],
    left_index=True, right_index=True, how='inner'
)
allrounder_df = allrounder_df[
    (allrounder_df['total_runs'] >= 500) &
    (allrounder_df['total_wickets'] >= 30) &
    (allrounder_df['matches_played'] >= 20) &
    (allrounder_df['matches_2plus_overs'] >= 20)
]
allrounder_df['allrounder_elo'] = np.sqrt(allrounder_df['batting_elo'] * allrounder_df['bowling_elo'])
allrounder_df.to_csv('allrounder_stats.csv')

# --- Fielding stats ---
fielding_df = pd.DataFrame(fielding_rows)
if not fielding_df.empty:
    fielding_stats = fielding_df.groupby('player')['event'].value_counts().unstack(fill_value=0)
    fielding_stats['total_fielding'] = fielding_stats.sum(axis=1)
    fielding_stats.to_csv('fielding_stats.csv')
else:
    pd.DataFrame().to_csv('fielding_stats.csv')  # Empty if no data

# --- Elite filtering (top 10%) ---
min_matches = 20
elite_batters = career_bat[career_bat['matches_played'] >= min_matches]
bat_thresh = elite_batters['batting_elo'].quantile(0.90)
elite_batters = elite_batters[elite_batters['batting_elo'] >= bat_thresh]
elite_batters.to_csv('elite_batters.csv')

elite_bowlers = career_bowl[
    (career_bowl['matches_2plus_overs'] >= 30) &
    (career_bowl['total_wickets'] >= 100) &
    (career_bowl['wickets_per_match'] >= 0.8) &
    (career_bowl['bowling_avg'] < 35) &
    (career_bowl['economy'] < 8.5)
]
bow_thresh = elite_bowlers['bowling_elo'].quantile(0.90)
elite_bowlers = elite_bowlers[elite_bowlers['bowling_elo'] >= bow_thresh]
elite_bowlers.to_csv('elite_bowlers.csv')

elo_thresh = allrounder_df['allrounder_elo'].quantile(0.90)
elite_allrounders = allrounder_df[allrounder_df['allrounder_elo'] >= elo_thresh]
elite_allrounders.to_csv('elite_allrounders.csv')

print("All CSVs saved.")
