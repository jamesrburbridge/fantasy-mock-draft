import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Fantasy Draft Board", layout="wide")

# The fully transcribed 16-round draft board based on your league's trades
DRAFT_ORDER = [
    # Round 1
    "A More Rippl", "Scarred From", "Done done done", "The Barding", "CMC Music Fa", "crimsan jhad", "merkle fully", "A More Rippl", "sackinbycorin", "Something Something Drake Maye", "Done done done", "Titans and Co",
    # Round 2
    "Titans and Co", "Team Emoji 🏈", "Something Something Drake Maye", "merkle fully", "Done done done", "crimsan jhad", "crimsan jhad", "Titans and Co", "The Barding", "Done done done", "Scarred From", "A More Rippl",
    # Round 3
    "A More Rippl", "Scarred From", "Done done done", "The Barding", "CMC Music Fa", "crimsan jhad", "merkle fully", "Scarred From", "merkle fully", "Something Something Drake Maye", "Done done done", "Titans and Co",
    # Round 4
    "Titans and Co", "A More Rippl", "Something Something Drake Maye", "sackinbycorin", "Big Penix En", "merkle fully", "Done done done", "CMC Music Fa", "The Barding", "Done done done", "Scarred From", "A More Rippl",
    # Round 5
    "Big Penix En", "Scarred From", "Big Penix En", "The Barding", "Titans and Co", "Titans and Co", "sackinbycorin", "Titans and Co", "sackinbycorin", "Something Something Drake Maye", "Team Emoji 🏈", "Titans and Co",
    # Round 6
    "Titans and Co", "Team Emoji 🏈", "Something Something Drake Maye", "sackinbycorin", "Done done done", "merkle fully", "crimsan jhad", "CMC Music Fa", "The Barding", "Done done done", "Scarred From", "A More Rippl",
    # Round 7
    "A More Rippl", "Big Penix En", "Done done done", "The Barding", "CMC Music Fa", "crimsan jhad", "merkle fully", "Big Penix En", "sackinbycorin", "Something Something Drake Maye", "Team Emoji 🏈", "Titans and Co",
    # Round 8
    "Titans and Co", "Team Emoji 🏈", "Something Something Drake Maye", "sackinbycorin", "Big Penix En", "sackinbycorin", "crimsan jhad", "CMC Music Fa", "The Barding", "Done done done", "Scarred From", "Team Emoji 🏈",
    # Round 9
    "A More Rippl", "Scarred From", "Done done done", "The Barding", "CMC Music Fa", "crimsan jhad", "merkle fully", "Titans and Co", "sackinbycorin", "Something Something Drake Maye", "Team Emoji 🏈", "Titans and Co",
    # Round 10
    "Titans and Co", "Team Emoji 🏈", "Something Something Drake Maye", "sackinbycorin", "Big Penix En", "merkle fully", "crimsan jhad", "CMC Music Fa", "The Barding", "Big Penix En", "Scarred From", "A More Rippl",
    # Round 11
    "A More Rippl", "Scarred From", "crimsan jhad", "The Barding", "CMC Music Fa", "crimsan jhad", "merkle fully", "Big Penix En", "sackinbycorin", "Something Something Drake Maye", "Team Emoji 🏈", "Titans and Co",
    # Round 12
    "crimsan jhad", "Team Emoji 🏈", "Something Something Drake Maye", "sackinbycorin", "Big Penix En", "merkle fully", "crimsan jhad", "CMC Music Fa", "The Barding", "Done done done", "Scarred From", "A More Rippl",
    # Round 13
    "A More Rippl", "Scarred From", "Done done done", "The Barding", "CMC Music Fa", "crimsan jhad", "merkle fully", "Big Penix En", "sackinbycorin", "Something Something Drake Maye", "Team Emoji 🏈", "Big Penix En",
    # Round 14
    "Big Penix En", "Team Emoji 🏈", "Something Something Drake Maye", "sackinbycorin", "Big Penix En", "merkle fully", "crimsan jhad", "CMC Music Fa", "The Barding", "Done done done", "Scarred From", "A More Rippl",
    # Round 15
    "A More Rippl", "Scarred From", "Team Emoji 🏈", "The Barding", "CMC Music Fa", "crimsan jhad", "merkle fully", "Big Penix En", "sackinbycorin", "Something Something Drake Maye", "Team Emoji 🏈", "CMC Music Fa",
    # Round 16
    "CMC Music Fa", "Team Emoji 🏈", "Something Something Drake Maye", "sackinbycorin", "Big Penix En", "merkle fully", "crimsan jhad", "CMC Music Fa", "The Barding", "Team Emoji 🏈", "Scarred From", "A More Rippl"
]

@st.cache_data
def load_data():
    df = pd.read_csv('fantasy_football_rankings.csv')
    df = df[['Player', 'Position', 'Team', 'Tier', 'Consensus', 'ADP']].copy()
    
    # Calculate Positional Rank
    df['Pos_Rank'] = df.groupby('Position')['Consensus'].rank(method='min')
    
    # Baseline Replacement Levels for a 12-team 2QB/Superflex setup
    baselines = {'QB': 28, 'RB': 48, 'WR': 60, 'TE': 16, 'K': 12, 'DST': 12}
    
    rep_values = {}
    for pos, base_rank in baselines.items():
        pos_df = df[df['Position'] == pos]
        if len(pos_df) >= base_rank:
            rep_values[pos] = pos_df[pos_df['Pos_Rank'] == base_rank].iloc[0]['Consensus']
        else:
            rep_values[pos] = pos_df['Consensus'].max() if not pos_df.empty else 100
            
    df['VOR'] = df['Position'].map(rep_values) - df['Consensus']
    return df.sort_values('VOR', ascending=False).reset_index(drop=True)

df_rankings = load_data()

# Initialize session state for drafted players
if 'drafted' not in st.session_state:
    st.session_state.drafted = [None] * 192

st.title("🏈 Fantasy Mock Draft Tool")

# Find the next available pick
current_pick_idx = next((i for i, x in enumerate(st.session_state.drafted) if x is None), 192)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Draft Controls")
    if current_pick_idx < 192:
        current_team = DRAFT_ORDER[current_pick_idx]
        st.subheader(f"On the Clock: {current_team}")
        st.write(f"Round {(current_pick_idx // 12) + 1}, Pick {(current_pick_idx % 12) + 1}")
        
        # Filter available players
        drafted_players = [p for p in st.session_state.drafted if p is not None]
        available_df = df_rankings[~df_rankings['Player'].isin(drafted_players)]
        
        selected_player = st.selectbox("Select Player to Draft:", available_df['Player'].tolist())
        
        if st.button("Draft Player"):
            st.session_state.drafted[current_pick_idx] = selected_player
            st.rerun()
    else:
        st.success("Draft Complete!")

    if st.button("Undo Last Pick"):
        if current_pick_idx > 0:
            st.session_state.drafted[current_pick_idx - 1] = None
            st.rerun()
            
    st.markdown("---")
    st.subheader("Your Upcoming Picks")
    my_picks = [(i, (i // 12) + 1, (i % 12) + 1) for i, team in enumerate(DRAFT_ORDER) if team == "Something Something Drake Maye"]
    for idx, rd, pk in my_picks:
        status = f"✅ Drafted: {st.session_state.drafted[idx]}" if st.session_state.drafted[idx] else "⏳ Pending"
        st.write(f"**Round {rd}, Pick {pk}** (Overall {idx+1}) - {status}")

with col2:
    tab1, tab2, tab3 = st.tabs(["Available Players", "Full Draft Board", "Team Dashboard (VOR)"])
    
    with tab1:
        st.dataframe(available_df[['Player', 'Position', 'Team', 'Tier', 'VOR', 'ADP']], use_container_width=True, height=500)
        
    with tab2:
        # Construct Draft Board Matrix
        board = []
        for rd in range(16):
            row = []
            for pk in range(12):
                idx = rd * 12 + pk
                team = DRAFT_ORDER[idx]
                player = st.session_state.drafted[idx] or "-"
                row.append(f"{team}\n{player}")
            board.append(row)
        df_board = pd.DataFrame(board, columns=[f"Pick {i+1}" for i in range(12)], index=[f"Round {i+1}" for i in range(16)])
        st.dataframe(df_board, use_container_width=True)
        
    with tab3:
        # Calculate Team VOR
        team_rosters = {team: [] for team in set(DRAFT_ORDER)}
        for idx, player in enumerate(st.session_state.drafted):
            if player:
                team = DRAFT_ORDER[idx]
                player_vor = df_rankings[df_rankings['Player'] == player]['VOR'].values[0]
                team_rosters[team].append(player_vor)
                
        team_vor_totals = {team: sum(vors) for team, vors in team_rosters.items()}
        df_vor = pd.DataFrame(list(team_vor_totals.items()), columns=["Team", "Total VOR"]).sort_values("Total VOR", ascending=False)
        st.bar_chart(df_vor.set_index("Team"))