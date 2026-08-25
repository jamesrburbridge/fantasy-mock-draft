import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Live Vertical Mock Draft", layout="wide")

# Full 16-round draft order with trades
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

# Pre-assigned Keepers (0-indexed global slots)
INITIAL_KEEPERS = {
    15: "Justin Herbert", 40: "Chase Brown", 45: "Jaxon Smith-Njigba",
    56: "Chris Olave", 57: "Brock Bowers", 68: "Bo Nix", 70: "Travis Etienne",
    72: "Tyler Warren", 80: "Javonte Williams", 82: "Jaxson Dart",
    90: "Shedeur Sanders", 108: "Christian Watson", 114: "Bucky Irving",
    129: "Drake Maye", 131: "Tyler Shough", 135: "Daniel Jones",
    138: "Malik Willis", 139: "Parker Washington", 140: "Harold Fannin",
    141: "Michael Wilson", 142: "Emanuel Wilson", 150: "Kyle Pitts",
    157: "Quinshon Judkins", 163: "Colston Loveland"
}

MY_TEAM_NAME = "Something Something Drake Maye"
ROSTER_REQS = {'QB': 2, 'RB': 2, 'WR': 3, 'TE': 1, 'FLEX': 2}
TOTAL_STARTERS = sum(ROSTER_REQS.values())

@st.cache_data
def load_base_data():
    df = pd.read_csv('fantasy_football_rankings.csv')
    df = df[['Player', 'Position', 'Team', 'Bye', 'Tier', 'Consensus', 'ADP']].copy()
    df['Pos_Rank'] = df.groupby('Position')['Consensus'].rank(method='min')
    
    def estimate_points(row):
        pos, rank = row['Position'], row['Pos_Rank']
        base = {'QB': 380, 'RB': 300, 'WR': 280, 'TE': 220, 'K': 140, 'DST': 130}
        decay = {'QB': 0.025, 'RB': 0.020, 'WR': 0.015, 'TE': 0.030, 'K': 0.015, 'DST': 0.015}
        return base[pos] * math.exp(-decay[pos] * (rank - 1)) if pos in base else 0
        
    df['Est_Pts'] = df.apply(estimate_points, axis=1)
    return df

df_base = load_base_data()

if 'slots' not in st.session_state:
    st.session_state.slots = {i: None for i in range(192)}
    for idx, player in INITIAL_KEEPERS.items():
        st.session_state.slots[idx] = player
if 'keepers' not in st.session_state:
    st.session_state.keepers = set(INITIAL_KEEPERS.values())

# Find the next empty draft slot
next_pick_idx = next((i for i in range(192) if st.session_state.slots[i] is None), None)
taken_players = [p for p in st.session_state.slots.values() if p is not None]

# --- Layout ---
st.title("🏈 Fantasy Vertical Draft Board")

col1, col2, col3 = st.columns([1, 1.2, 1.3])

# ==========================================
# COLUMN 1: Vertical Draft Timeline
# ==========================================
with col1:
    st.subheader("Draft Timeline")
    
    timeline_data = []
    for i, team in enumerate(DRAFT_ORDER):
        rnd = (i // 12) + 1
        pk = (i % 12) + 1
        player = st.session_state.slots[i]
        
        status = ""
        if player in st.session_state.keepers:
            status = "🔒"
        elif player is None and i == next_pick_idx:
            status = "▶️ ON CLOCK"
        elif player is None:
            status = "..."
        else:
            status = player
            
        team_display = f"⭐ {team}" if team == MY_TEAM_NAME else team
        timeline_data.append({"Pick": f"{rnd}.{pk:02d}", "Team": team_display, "Selection": status})

    df_timeline = pd.DataFrame(timeline_data)
    st.dataframe(df_timeline, use_container_width=True, height=800)
    
    if st.button("⏪ Undo Last Draft Pick"):
        last_drafted_idx = next((i for i in reversed(range(192)) if st.session_state.slots[i] is not None and st.session_state.slots[i] not in st.session_state.keepers), None)
        if last_drafted_idx is not None:
            st.session_state.slots[last_drafted_idx] = None
            st.rerun()

# ==========================================
# COLUMN 2: Draft Controls & Available Players
# ==========================================
with col2:
    if next_pick_idx is not None:
        on_clock_team = DRAFT_ORDER[next_pick_idx]
        rnd, pk = (next_pick_idx // 12) + 1, (next_pick_idx % 12) + 1
        st.subheader(f"On The Clock: {on_clock_team}")
        st.caption(f"Round {rnd}, Pick {pk} (Overall {next_pick_idx + 1})")
        
        available_players_list = [p for p in df_base['Player'] if p not in taken_players]
        live_player = st.selectbox("Select Player to Draft:", available_players_list)
        
        if st.button("Draft Player", type="primary", use_container_width=True):
            st.session_state.slots[next_pick_idx] = live_player
            st.rerun()
    else:
        st.success("Draft Complete!")

    st.markdown("---")
    st.subheader("Available Players")
    
    # Live VOR Scarcity Logic (based on all taken players)
    removed_counts = df_base[df_base['Player'].isin(taken_players)]['Position'].value_counts().to_dict()
    available_df = df_base[~df_base['Player'].isin(taken_players)].copy()
    available_df['Pool_Pos_Rank'] = available_df.groupby('Position')['Consensus'].rank(method='min')

    total_needed = {'QB': 28, 'RB': 48, 'WR': 60, 'TE': 16, 'K': 12, 'DST': 12}
    rep_pts = {}
    for pos, base_total in total_needed.items():
        effective_target = max(1, base_total - removed_counts.get(pos, 0))
        pos_sub = available_df[available_df['Position'] == pos]
        rep_pts[pos] = pos_sub[pos_sub['Pool_Pos_Rank'] == effective_target].iloc[0]['Est_Pts'] if len(pos_sub) >= effective_target else (pos_sub['Est_Pts'].min() if not pos_sub.empty else 0)

    available_df['VOR'] = available_df.apply(lambda row: round(row['Est_Pts'] - rep_pts.get(row['Position'], 0), 1), axis=1)
    available_df = available_df.sort_values('VOR', ascending=False).reset_index(drop=True)
    
    # Allow filtering by position
    pos_filter = st.selectbox("Filter Position", ["All", "QB", "RB", "WR", "TE"])
    if pos_filter != "All":
        available_df = available_df[available_df['Position'] == pos_filter]

    st.dataframe(available_df[['Player', 'Position', 'Tier', 'VOR', 'ADP']], use_container_width=True, height=520)

# ==========================================
# COLUMN 3: Team Construction Tally
# ==========================================
with col3:
    st.subheader("Team Construction Tracker")
    
    team_names = sorted(list(set(DRAFT_ORDER)))
    needs_data = []
    
    for team in team_names:
        team_picks = [st.session_state.slots[i] for i, t in enumerate(DRAFT_ORDER) if t == team and st.session_state.slots[i]]
        counts = df_base[df_base['Player'].isin(team_picks)]['Position'].value_counts().to_dict()
        
        qbs, rbs, wrs, tes = counts.get('QB', 0), counts.get('RB', 0), counts.get('WR', 0), counts.get('TE', 0)
        
        # Calculate completion of core starter requirements (does not count kickers/DST for primary health check)
        core_starters_filled = min(qbs, 2) + min(rbs, 2) + min(wrs, 3) + min(tes, 1)
        # Flex check (any RB/WR/TE beyond minimums)
        flex_candidates = max(0, rbs - 2) + max(0, wrs - 3) + max(0, tes - 1)
        core_starters_filled += min(flex_candidates, 2)
        
        completion_pct = round((core_starters_filled / TOTAL_STARTERS) * 100)
        
        urgencies = []
        if qbs < 2: urgencies.append(f"QB ({2-qbs})")
        if rbs < 2: urgencies.append(f"RB ({2-rbs})")
        if wrs < 3: urgencies.append(f"WR ({3-wrs})")
        if tes < 1: urgencies.append(f"TE (1)")
        
        needs_data.append({
            "Team": "⭐ " + team if team == MY_TEAM_NAME else team,
            "Completeness": f"{completion_pct}%",
            "QB": qbs, "RB": rbs, "WR": wrs, "TE": tes,
            "Urgent Starter Needs": ", ".join(urgencies) if urgencies else "Bench/Flex"
        })
        
    df_needs = pd.DataFrame(needs_data)
    
    # Stylize the completeness output visually
    st.dataframe(df_needs, use_container_width=True, height=450)
    
    st.markdown("---")
    st.subheader(f"My Roster Tracker")
    my_players = [st.session_state.slots[i] for i, t in enumerate(DRAFT_ORDER) if t == MY_TEAM_NAME and st.session_state.slots[i]]
    if my_players:
        st.dataframe(df_base[df_base['Player'].isin(my_players)][['Player', 'Position', 'Bye']], use_container_width=True)
    else:
        st.write("No players drafted yet.")