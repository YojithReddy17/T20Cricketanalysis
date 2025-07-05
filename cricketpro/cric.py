import os
st.write("Current working directory:", os.getcwd())
st.write("Files in directory:", os.listdir())


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="T20 Player Elo Analytics Dashboard", layout="wide")
st.title("T20 Player Elo Analytics Dashboard")

@st.cache_data
def load_csv(name):
    if not os.path.exists(name):
        st.error(f"File '{name}' not found. Please run the pipeline first.")
        st.stop()
    return pd.read_csv(name, index_col=0)

with st.spinner("Loading data..."):
    batting = load_csv('batting_stats.csv')
    bowling = load_csv('bowling_stats.csv')
    allrounders = load_csv('allrounder_stats.csv')
    elite_batters = load_csv('elite_batters.csv')
    elite_bowlers = load_csv('elite_bowlers.csv')
    elite_allrounders = load_csv('elite_allrounders.csv')
    elo_batting_hist = pd.read_csv('elo_history_batting.csv')
    elo_bowling_hist = pd.read_csv('elo_history_bowling.csv')
    fielding_stats = load_csv('fielding_stats.csv')

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Batters", "Bowlers", "All-Rounders", "Player Details", "Compare Players", "Top 20 Elo Progression"
])

with tab1:
    st.header("Batters")
    show_elite = st.checkbox("Show only elite batters", value=True, key="elite_batters")
    data = elite_batters if show_elite else batting
    cols = ['batting_elo', 'total_runs', 'matches_played', 'bat_avg', 'strike_rate', 'milestone_1000_runs']
    available_cols = [col for col in cols if col in data.columns]
    st.dataframe(
        data.sort_values('batting_elo', ascending=False)[available_cols].head(50 if show_elite else 100),
        use_container_width=True
    )
    st.download_button(
        label="Download Batting Data as CSV",
        data=data.to_csv().encode('utf-8'),
        file_name='batting_stats.csv',
        mime='text/csv'
    )
    st.plotly_chart(px.histogram(data, x="batting_elo", nbins=30, title="Batting Elo Distribution"), use_container_width=True, key="bat_hist")
    st.plotly_chart(px.scatter(data, x="batting_elo", y="strike_rate", hover_name=data.index, title="Batting Elo vs Strike Rate"), use_container_width=True, key="bat_scatter")

with tab2:
    st.header("Bowlers")
    show_elite = st.checkbox("Show only elite bowlers", value=True, key="elite_bowlers")
    data = elite_bowlers if show_elite else bowling
    cols = ['bowling_elo', 'total_wickets', 'matches_2plus_overs', 'bowling_avg', 'economy', 'wickets_per_match', 'milestone_100_wickets']
    available_cols = [col for col in cols if col in data.columns]
    st.dataframe(
        data.sort_values('bowling_elo', ascending=False)[available_cols].head(50 if show_elite else 100),
        use_container_width=True
    )
    st.download_button(
        label="Download Bowling Data as CSV",
        data=data.to_csv().encode('utf-8'),
        file_name='bowling_stats.csv',
        mime='text/csv'
    )
    st.plotly_chart(px.histogram(data, x="bowling_elo", nbins=30, title="Bowling Elo Distribution"), use_container_width=True, key="bowl_hist")
    st.plotly_chart(px.scatter(data, x="bowling_elo", y="economy", hover_name=data.index, title="Bowling Elo vs Economy"), use_container_width=True, key="bowl_scatter")

with tab3:
    st.header("All-Rounders")
    show_elite = st.checkbox("Show only elite all-rounders", value=True, key="elite_allrounders")
    data = elite_allrounders if show_elite else allrounders
    cols = ['allrounder_elo', 'batting_elo', 'bowling_elo', 'total_runs', 'total_wickets', 'matches_played', 'matches_2plus_overs']
    available_cols = [col for col in cols if col in data.columns]
    st.dataframe(
        data.sort_values('allrounder_elo', ascending=False)[available_cols].head(50 if show_elite else 100),
        use_container_width=True
    )
    st.download_button(
        label="Download All-Rounder Data as CSV",
        data=data.to_csv().encode('utf-8'),
        file_name='allrounder_stats.csv',
        mime='text/csv'
    )
    st.plotly_chart(px.histogram(data, x="allrounder_elo", nbins=30, title="All-Rounder Elo Distribution"), use_container_width=True, key="ar_hist")

with tab4:
    st.header("Player Details & Career Graphs")
    all_players = sorted(set(batting.index) | set(bowling.index))
    player = st.selectbox("Search for a player", all_players, key="player_details_search")

    st.subheader(f"Batting Stats for {player}")
    if player in batting.index:
        st.table(batting.loc[[player]][['batting_elo', 'total_runs', 'matches_played', 'bat_avg', 'strike_rate', 'milestone_1000_runs']])
    else:
        st.info("No batting stats available.")

    st.subheader(f"Bowling Stats for {player}")
    if player in bowling.index:
        st.table(bowling.loc[[player]][['bowling_elo', 'total_wickets', 'matches_2plus_overs', 'bowling_avg', 'economy', 'wickets_per_match', 'milestone_100_wickets']])
    else:
        st.info("No bowling stats available.")

    st.subheader(f"Fielding Stats for {player}")
    if player in fielding_stats.index:
        stats = fielding_stats.loc[[player]]
        stats = stats.loc[:, (stats != 0).any(axis=0)]
        st.table(stats)
    else:
        st.info("No fielding stats available.")

    st.subheader(f"Batting Elo Progression for {player}")
    if 'batter' in elo_batting_hist.columns and player in elo_batting_hist['batter'].values:
        df_bat = elo_batting_hist[elo_batting_hist['batter'] == player]
        if not df_bat.empty:
            st.plotly_chart(
                px.line(df_bat, x="date", y="batting_elo", title=f"{player} - Batting Elo Over Time"),
                use_container_width=True,
                key=f"bat_elo_{player}"
            )
        else:
            st.info("No Batting Elo history available for this player.")
    else:
        st.info("No Batting Elo history available for this player.")

    st.subheader(f"Bowling Elo Progression for {player}")
    if 'bowler' in elo_bowling_hist.columns and player in elo_bowling_hist['bowler'].values:
        df_bowl = elo_bowling_hist[elo_bowling_hist['bowler'] == player]
        if not df_bowl.empty:
            st.plotly_chart(
                px.line(df_bowl, x="date", y="bowling_elo", title=f"{player} - Bowling Elo Over Time"),
                use_container_width=True,
                key=f"bowl_elo_{player}"
            )
        else:
            st.info("No Bowling Elo history available for this player.")
    else:
        st.info("No Bowling Elo history available for this player.")

with tab5:
    st.header("Compare Two Players")
    all_players = sorted(set(batting.index) | set(bowling.index))
    player1 = st.selectbox("Player 1", all_players, key="p1")
    player2 = st.selectbox("Player 2", all_players, key="p2")
    st.subheader(f"Comparison: {player1} vs {player2}")

    stats = []
    for player in [player1, player2]:
        bat = batting.loc[player] if player in batting.index else None
        bowl = bowling.loc[player] if player in bowling.index else None
        stats.append({
            "Batting Elo": bat['batting_elo'] if bat is not None else None,
            "Total Runs": bat['total_runs'] if bat is not None else None,
            "Bat Avg": bat['bat_avg'] if bat is not None else None,
            "Strike Rate": bat['strike_rate'] if bat is not None else None,
            "Bowling Elo": bowl['bowling_elo'] if bowl is not None else None,
            "Total Wickets": bowl['total_wickets'] if bowl is not None else None,
            "Bowling Avg": bowl['bowling_avg'] if bowl is not None else None,
            "Economy": bowl['economy'] if bowl is not None else None
        })
    st.dataframe(pd.DataFrame(stats, index=[player1, player2]))

    st.subheader("Batting Elo Progression Comparison")
    fig = go.Figure()
    for idx, player in enumerate([player1, player2]):
        if 'batter' in elo_batting_hist.columns and player in elo_batting_hist['batter'].values:
            df = elo_batting_hist[elo_batting_hist['batter'] == player]
            fig.add_trace(go.Scatter(x=df['date'], y=df['batting_elo'], mode='lines', name=player))
    fig.update_layout(title="Batting Elo Progression", xaxis_title="Date", yaxis_title="Batting Elo")
    st.plotly_chart(fig, use_container_width=True, key="bat_compare")

    st.subheader("Bowling Elo Progression Comparison")
    fig = go.Figure()
    for idx, player in enumerate([player1, player2]):
        if 'bowler' in elo_bowling_hist.columns and player in elo_bowling_hist['bowler'].values:
            df = elo_bowling_hist[elo_bowling_hist['bowler'] == player]
            fig.add_trace(go.Scatter(x=df['date'], y=df['bowling_elo'], mode='lines', name=player))
    fig.update_layout(title="Bowling Elo Progression", xaxis_title="Date", yaxis_title="Bowling Elo")
    st.plotly_chart(fig, use_container_width=True, key="bowl_compare")

with tab6:
    st.header("Top 20 Elo Progression")
    st.subheader("Batters: Elo Progression for Top 20")
    top20_batters = batting.sort_values('batting_elo', ascending=False).head(20).index
    fig = go.Figure()
    for player in top20_batters:
        if 'batter' in elo_batting_hist.columns and player in elo_batting_hist['batter'].values:
            df = elo_batting_hist[elo_batting_hist['batter'] == player]
            fig.add_trace(go.Scatter(x=df['date'], y=df['batting_elo'], mode='lines', name=player))
    fig.update_layout(title="Top 20 Batters - Batting Elo Progression", xaxis_title="Date", yaxis_title="Batting Elo")
    st.plotly_chart(fig, use_container_width=True, key="top20_bat")

    st.subheader("Bowlers: Elo Progression for Top 20")
    top20_bowlers = bowling.sort_values('bowling_elo', ascending=False).head(20).index
    fig = go.Figure()
    for player in top20_bowlers:
        if 'bowler' in elo_bowling_hist.columns and player in elo_bowling_hist['bowler'].values:
            df = elo_bowling_hist[elo_bowling_hist['bowler'] == player]
            fig.add_trace(go.Scatter(x=df['date'], y=df['bowling_elo'], mode='lines', name=player))
    fig.update_layout(title="Top 20 Bowlers - Bowling Elo Progression", xaxis_title="Date", yaxis_title="Bowling Elo")
    st.plotly_chart(fig, use_container_width=True, key="top20_bowl")

    st.subheader("All-Rounders: Elo Progression for Top 20")
    top20_ars = allrounders.sort_values('allrounder_elo', ascending=False).head(20).index
    fig = go.Figure()
    for player in top20_ars:
        if 'batter' in elo_batting_hist.columns and player in elo_batting_hist['batter'].values:
            df = elo_batting_hist[elo_batting_hist['batter'] == player]
            fig.add_trace(go.Scatter(x=df['date'], y=df['batting_elo'], mode='lines', name=player))
    fig.update_layout(title="Top 20 All-Rounders - Batting Elo Progression", xaxis_title="Date", yaxis_title="Batting Elo")
    st.plotly_chart(fig, use_container_width=True, key="top20_ar")

st.markdown("---")
st.markdown("**Powered by Streamlit & Plotly | Research-backed T20 analytics**")
