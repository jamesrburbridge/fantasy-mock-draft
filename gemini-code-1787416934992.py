import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Draft Board & Scarcity Dashboard", layout="wide")

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

@st.cache_data
def load_base_data():
    df = pd.read_csv('fantasy_football_rankings.csv')
    df = df[['Player', 'Position', 'Team', 'Bye', 'Tier', 'Consensus', 'ADP']].copy()
    df['Pos_Rank'] = df.groupby('Position')['Consensus'].rank(method='min')
    def estimate_points(row):
        pos = row['Position']
        rank = row['Pos_Rank']
        base = {'QB': 380, 'RB': 300, 'WR': 280, 'TE': 220, 'K': 140, 'DST': 130}
        decay = {'QB': 0.025, 'RB': 0.020, 'WR': 0.015, 'TE': 0.030, 'K': 0.015, 'DST': 0.015}
        if pos in base: return base[pos] * math.exp(-decay[pos] * (rank - 1))
        return 0
    df['Est_Pts'] = df.apply(estimate_points, axis=1)
    return df

df_base = load_base_data()

if 'slots' not in st.session_state:
    st.session_state.slots = {i: None for i in range(192)}
    for idx, player in INITIAL_KEEPERS.items():
        st.session_state.slots[idx] = player
if 'keepers' not in st.session_state:
    st.session_state.keepers = set(INITIAL_KEEPERS.values())

# --- Sidebar ---
st.sidebar.title("Draft Settings")
vor_mode = st.sidebar.radio("VOR Scarcity Mode", ["Keeper-Adjusted Baseline", "Live Dynamic"])
st.sidebar.markdown("---")
slot_labels = {i: f"{(i // 12) + 1}.{(i % 12) + 1:02d} ({t})" for i, t in enumerate(DRAFT_ORDER)}
selected_slot_idx = st.sidebar.selectbox("Assign Player to Slot", options=list(slot_labels.keys()), format_func=lambda x: slot_labels[x])
taken_players = [p for p in st.session_state.slots.values() if p is not None]
available_players_list = ["(Clear Slot)"] + [p for p in df_base['Player'] if p not in taken_players]
selected_player = st.sidebar.selectbox("Select Player", available_players_list)
is_keeper_check = st.sidebar.checkbox("Mark as Keeper", value=True)

if st.sidebar.button("Assign / Save", use_container_width=True):
    if selected_player == "(Clear Slot)":
        prev = st.session_state.slots[selected_slot_idx]
        st.session_state.slots[selected_slot_idx] = None
        if prev in st.session_state.keepers: st.session_state.keepers.remove(prev)
    else:
        st.session_state.slots[selected_slot_idx] = selected_player
        if is_keeper_check: st.session_state.keepers.add(selected_player)
        elif selected_player in st.session_state.keepers: st.session_state.keepers.remove(selected_player)
    st.rerun()

next_pick_idx = next((i for i in range(192) if st.session_state.slots[i] is None), None)
if next_pick_idx is not None:
    st.sidebar.markdown("---")
    st.sidebar.write(f"**On Clock:** {slot_labels[next_pick_idx]}")
    live_player = st.sidebar.selectbox("Draft Next Player", [p for p in df_base['Player'] if p not in taken_players], key="live_pick")
    if st.sidebar.button("Draft Pick", type="primary"):
        st.session_state.slots[next_pick_idx] = live_player
        st.rerun()

# --- Scarcity Data Prep ---
removed_players = taken_players if "Live" in vor_mode else list(st.session_state.keepers)
removed_counts = df_base[df_base['Player'].isin(removed_players)]['Position'].value_counts().to_dict()
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

# --- Layout Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["Draft Board Grid", "Available Players", "My Team & Byes", "League Needs & Threats"])

with tab1:
    board_display = []
    for rnd in range(16):
        row_data = {}
        for pk in range(12):
            idx = rnd * 12 + pk
            team = DRAFT_ORDER[idx]
            player = st.session_state.slots[idx]
            p_text = f"🔒 {player}" if player and player in st.session_state.keepers else (player if player else "---")
            
            # Formats the cell to explicitly show Team Name above the player pick
            cell_val = f"⭐ {team} \n {p_text}" if team == MY_TEAM_NAME else f"{team} \n {p_text}"
            row_data[f"Pick {pk+1}"] = cell_val
        board_display.append(row_data)
        
    st.dataframe(pd.DataFrame(board_display, index=[f"Round {r+1}" for r in range(16)]), use_container_width=True, height=650)

with tab2:
    st.dataframe(available_df[['Player', 'Position', 'Tier', 'Bye', 'VOR', 'ADP']], use_container_width=True, height=550)

with tab3:
    st.subheader(f"My Roster: {MY_TEAM_NAME}")
    my_players = [st.session_state.slots[i] for i, t in enumerate(DRAFT_ORDER) if t == MY_TEAM_NAME and st.session_state.slots[i]]
    my_roster_df = df_base[df_base['Player'].isin(my_players)]
    st.dataframe(my_roster_df[['Player', 'Position', 'Bye', 'Tier']], use_container_width=True)
    
    byes = my_roster_df['Bye'].dropna().tolist()
    dupes = set([x for x in byes if byes.count(x) > 1])
    if dupes: st.error(f"⚠️ Bye Week Conflict Detected on Weeks: {', '.join([str(int(w)) for w in dupes])}")

with tab4:
    st.subheader("📊 League Positional Composition")
    team_names = sorted(list(set(DRAFT_ORDER)))
    needs_data = []
    
    for team in team_names:
        team_picks = [st.session_state.slots[i] for i, t in enumerate(DRAFT_ORDER) if t == team and st.session_state.slots[i]]
        counts = df_base[df_base['Player'].isin(team_picks)]['Position'].value_counts().to_dict()
        
        qbs, rbs, wrs, tes = counts.get('QB', 0), counts.get('RB', 0), counts.get('WR', 0), counts.get('TE', 0)
        
        urgencies = []
        if qbs < ROSTER_REQS['QB']: urgencies.append(f"QB ({ROSTER_REQS['QB']-qbs})")
        if rbs < ROSTER_REQS['RB']: urgencies.append(f"RB ({ROSTER_REQS['RB']-rbs})")
        if wrs < ROSTER_REQS['WR']: urgencies.append(f"WR ({ROSTER_REQS['WR']-wrs})")
        if tes < ROSTER_REQS['TE']: urgencies.append("TE (1)")
        
        needs_data.append({
            "Team": team, "QB": qbs, "RB": rbs, "WR": wrs, "TE": tes,
            "Urgent Starter Needs": ", ".join(urgencies) if urgencies else "Depth"
        })
        
    df_needs = pd.DataFrame(needs_data)
    st.dataframe(df_needs, use_container_width=True, height=450)

    st.markdown("---")
    st.subheader("🎯 Upcoming Turn Threat Radar")
    
    my_indices = [i for i, t in enumerate(DRAFT_ORDER) if t == MY_TEAM_NAME]
    upcoming = [i for i in my_indices if i >= (next_pick_idx or 0)]
    
    if len(upcoming) >= 2:
        start_idx, end_idx = upcoming[0], upcoming[1]
        intervening_teams = [DRAFT_ORDER[i] for i in range(start_idx + 1, end_idx)]
        st.write(f"**Teams picking before your next slot ({slot_labels[end_idx]}):** {len(intervening_teams)}")
        
        intervening_needs = df_needs[df_needs['Team'].isin(intervening_teams)]
        st.dataframe(intervening_needs[['Team', 'Urgent Starter Needs']], use_container_width=True)

        st.markdown("**Automated Tier-Run Alerts:**")
        for pos in ['QB', 'RB', 'WR', 'TE']:
            pos_df = available_df[available_df['Position'] == pos]
            if pos_df.empty: continue
            
            top_tier = pos_df['Tier'].min()
            tier_count = len(pos_df[pos_df['Tier'] == top_tier])
            
            teams_needing_pos = sum(1 for _, row in intervening_needs.iterrows() if pos in row['Urgent Starter Needs'])
            
            if teams_needing_pos >= tier_count and tier_count > 0:
                st.error(f"🚨 **Run Risk:** {teams_needing_pos} intervening teams need a {pos}, and there are only {tier_count} Tier {int(top_tier)} {pos}s left!")
            elif teams_needing_pos > 0 and tier_count <= 2:
                st.warning(f"⚠️ **Scarcity Warning:** {teams_needing_pos} team(s) need a {pos}, and only {tier_count} Tier {int(top_tier)} {pos}s remain.")
    else:
        st.write("Not enough future draft picks to calculate radar.")