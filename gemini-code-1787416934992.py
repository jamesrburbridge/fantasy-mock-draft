import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fantasy Mock Draft & Scarcity Dashboard", layout="wide")

# Full 16-round draft board based on your league's trades
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
def load_base_data():
    df = pd.read_csv('fantasy_football_rankings.csv')
    df = df[['Player', 'Position', 'Team', 'Tier', 'Consensus', 'ADP']].copy()
    
    # Calculate initial Positional Rank in overall pool
    df['Pos_Rank'] = df.groupby('Position')['Consensus'].rank(method='min')
    
    # 2QB / Superflex Scarcity Point Curve Model
    def estimate_points(row):
        pos = row['Position']
        rank = row['Pos_Rank']
        
        base = {'QB': 380, 'RB': 300, 'WR': 280, 'TE': 220, 'K': 140, 'DST': 130}
        decay = {'QB': 0.025, 'RB': 0.020, 'WR': 0.015, 'TE': 0.030, 'K': 0.015, 'DST': 0.015}
        
        if pos in base:
            return base[pos] * math.exp(-decay[pos] * (rank - 1))
        return 0
        
    df['Est_Pts'] = df.apply(estimate_points, axis=1)
    return df

df_base = load_base_data()

# Initialize slots in session state
if 'slots' not in st.session_state:
    st.session_state.slots = {i: None for i in range(192)}

if 'keepers' not in st.session_state:
    st.session_state.keepers = set()

# -----------------
# SIDEBAR CONTROLS
# -----------------
st.sidebar.title("Draft Settings & Controls")

vor_mode = st.sidebar.radio(
    "VOR Scarcity Mode",
    ["Keeper-Adjusted Baseline (Roadmap)", "Live Dynamic (Real-Time Run Tracker)"],
    help="Keeper-Adjusted locks the baseline after accounting for keepers. Live Dynamic constantly adjusts baselines as picks are made."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Assign Keepers / Slot Picks")

slot_labels = {}
for i, team in enumerate(DRAFT_ORDER):
    rnd = (i // 12) + 1
    pick = (i % 12) + 1
    slot_labels[i] = f"{rnd}.{pick:02d} ({team})"

selected_slot_idx = st.sidebar.selectbox("Select Draft Slot", options=list(slot_labels.keys()), format_func=lambda x: slot_labels[x])

taken_players = [p for p in st.session_state.slots.values() if p is not None]
available_players_list = ["(Clear Slot)"] + [p for p in df_base['Player'] if p not in taken_players]

selected_player = st.sidebar.selectbox("Select Player", available_players_list)
is_keeper_check = st.sidebar.checkbox("Mark as Keeper", value=True)

col_k1, col_k2 = st.sidebar.columns(2)
if col_k1.button("Assign / Save", use_container_width=True):
    if selected_player == "(Clear Slot)":
        prev_player = st.session_state.slots[selected_slot_idx]
        st.session_state.slots[selected_slot_idx] = None
        if prev_player in st.session_state.keepers:
            st.session_state.keepers.remove(prev_player)
    else:
        st.session_state.slots[selected_slot_idx] = selected_player
        if is_keeper_check:
            st.session_state.keepers.add(selected_player)
        elif selected_player in st.session_state.keepers:
            st.session_state.keepers.remove(selected_player)
    st.rerun()

# Quick Pick for on-the-clock drafting
st.sidebar.markdown("---")
st.sidebar.subheader("Live Draft Clock")
next_pick_idx = next((i for i in range(192) if st.session_state.slots[i] is None), None)

if next_pick_idx is not None:
    st.sidebar.write(f"**On the Clock:** {slot_labels[next_pick_idx]}")
    live_player = st.sidebar.selectbox("Draft Next Player", [p for p in df_base['Player'] if p not in taken_players], key="live_pick")
    if st.sidebar.button("Draft Pick", type="primary", use_container_width=True):
        st.session_state.slots[next_pick_idx] = live_player
        st.rerun()
else:
    st.sidebar.success("Draft Complete!")

if st.sidebar.button("Reset Entire Board"):
    st.session_state.slots = {i: None for i in range(192)}
    st.session_state.keepers = set()
    st.rerun()


# -----------------
# VOR CALCULATION ENGINE
# -----------------
total_needed = {'QB': 28, 'RB': 48, 'WR': 60, 'TE': 16, 'K': 12, 'DST': 12}

if "Live Dynamic" in vor_mode:
    # Baseline adjusts based on ALL taken players so far
    removed_players = taken_players
else:
    # Baseline adjusts ONLY based on designated Keepers
    removed_players = list(st.session_state.keepers)

# Calculate removed counts by position
removed_df = df_base[df_base['Player'].isin(removed_players)]
removed_counts = removed_df['Position'].value_counts().to_dict()

# Calculate remaining pool and new VOR
available_df = df_base[~df_base['Player'].isin(taken_players)].copy()
available_df['Pool_Pos_Rank'] = available_df.groupby('Position')['Consensus'].rank(method='min')

rep_pts = {}
for pos, base_total in total_needed.items():
    effective_target = max(1, base_total - removed_counts.get(pos, 0))
    pos_sub = available_df[available_df['Position'] == pos]
    if len(pos_sub) >= effective_target:
        rep_pts[pos] = pos_sub[pos_sub['Pool_Pos_Rank'] == effective_target].iloc[0]['Est_Pts']
    else:
        rep_pts[pos] = pos_sub['Est_Pts'].min() if not pos_sub.empty else 0

available_df['VOR'] = available_df.apply(
    lambda row: round(row['Est_Pts'] - rep_pts.get(row['Position'], 0), 1), axis=1
)
available_df = available_df.sort_values('VOR', ascending=False).reset_index(drop=True)


# -----------------
# MAIN DASHBOARD TABS
# -----------------
st.title("🏈 Fantasy Mock Draft Grid & Dynamic Scarcity Board")

tab1, tab2 = st.tabs(["Draft Board Grid", "Available Players & Scarcity Dashboard"])

with tab1:
    st.markdown("### Draft Board")
    st.caption("Picks marked with 🔒 are designated Keepers. ⭐ indicates your draft picks.")
    
    board_display = []
    for rnd in range(16):
        row_data = {}
        for pk in range(12):
            idx = rnd * 12 + pk
            team = DRAFT_ORDER[idx]
            player = st.session_state.slots[idx]
            
            cell_text = player if player else "-"
            if player and player in st.session_state.keepers:
                cell_text = f"🔒 {cell_text}"
            if team == "Something Something Drake Maye":
                cell_text = f"⭐ {cell_text}"
                
            row_data[f"Pick {pk+1}"] = cell_text
        board_display.append(row_data)

    df_board = pd.DataFrame(board_display, index=[f"Round {r+1}" for r in range(16)])
    st.dataframe(df_board, use_container_width=True, height=580)

with tab2:
    st.subheader(f"Available Players ({vor_mode})")
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    qbs_left = len(available_df[available_df['Position'] == 'QB'])
    rbs_left = len(available_df[available_df['Position'] == 'RB'])
    wrs_left = len(available_df[available_df['Position'] == 'WR'])
    tes_left = len(available_df[available_df['Position'] == 'TE'])
    
    col_kpi1.metric("Available QBs", qbs_left)
    col_kpi2.metric("Available RBs", rbs_left)
    col_kpi3.metric("Available WRs", wrs_left)
    col_kpi4.metric("Available TEs", tes_left)
    
    st.dataframe(
        available_df[['Player', 'Position', 'Team', 'Tier', 'Pos_Rank', 'VOR', 'ADP']],
        use_container_width=True,
        height=500
    )