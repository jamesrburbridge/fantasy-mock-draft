import streamlit as st
import pandas as pd

st.set_page_config(page_title="Grid Draft Board & Keepers", layout="wide")

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
def load_data():
    df = pd.read_csv('fantasy_football_rankings.csv')
    df = df[['Player', 'Position', 'Team', 'Tier', 'Consensus', 'ADP']].copy()
    
    # Calculate Positional Rank
    df['Pos_Rank'] = df.groupby('Position')['Consensus'].rank(method='min')
    
    # Baseline Replacement Levels (2QB, 2FLEX = deeper starting rosters)
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

# Session State for draft slot allocations (192 total picks)
if 'slots' not in st.session_state:
    st.session_state.slots = {i: None for i in range(192)}

st.title("🏈 Keeper / Mock Draft Grid")

# -----------------
# 1. SLOT MANAGER (KEEPER & DRAFT INPUT)
# -----------------
st.sidebar.header("Assign Players to Slots")
st.sidebar.markdown("Use this to lock in keepers or manually assign picks anywhere on the board.")

# Generate labels for all 192 picks
slot_labels = {}
for i, team in enumerate(DRAFT_ORDER):
    rnd = (i // 12) + 1
    pick = (i % 12) + 1
    slot_labels[i] = f"{rnd}.{pick:02d} ({team})"

# Dropdown to select a specific slot to edit
selected_slot_idx = st.sidebar.selectbox("Select Draft Slot", options=list(slot_labels.keys()), format_func=lambda x: slot_labels[x])

# Filter out players already assigned anywhere on the board
drafted_players = [p for p in st.session_state.slots.values() if p is not None]
available_df = df_rankings[~df_rankings['Player'].isin(drafted_players)]
available_players = ["(Clear Slot)"] + available_df['Player'].tolist()

selected_player = st.sidebar.selectbox("Select Player to Assign", available_players)

col1, col2 = st.sidebar.columns(2)
if col1.button("Assign / Keep", use_container_width=True):
    if selected_player == "(Clear Slot)":
        st.session_state.slots[selected_slot_idx] = None
    else:
        st.session_state.slots[selected_slot_idx] = selected_player
    st.rerun()

# Quick Assign feature for standard drafting (next available empty slot)
st.sidebar.markdown("---")
st.sidebar.subheader("Live Draft (Next Empty Pick)")
next_pick_idx = next((i for i in range(192) if st.session_state.slots[i] is None), None)

if next_pick_idx is not None:
    st.sidebar.write(f"**On the Clock:** {slot_labels[next_pick_idx]}")
    live_player = st.sidebar.selectbox("Select Player", available_df['Player'].tolist(), key="live_draft_select")
    if st.sidebar.button("Draft Player", type="primary"):
        st.session_state.slots[next_pick_idx] = live_player
        st.rerun()
else:
    st.sidebar.success("Draft Board is full!")


# -----------------
# 2. DRAFT BOARD GRID & DASHBOARD
# -----------------
tab1, tab2 = st.tabs(["Draft Board Grid", "Available Player Dashboard"])

with tab1:
    st.markdown("### The Board")
    st.markdown("Picks belonging to **Something Something Drake Maye** are highlighted.")
    
    # Build a DataFrame representing the 16x12 grid
    board_display = []
    for rnd in range(16):
        row_data = {}
        for pk in range(12):
            idx = rnd * 12 + pk
            team = DRAFT_ORDER[idx]
            player = st.session_state.slots[idx]
            
            # Formatting the cell content
            cell_text = player if player else "-"
            # Add star emoji for your picks to make them stand out
            if team == "Something Something Drake Maye":
                cell_text = f"⭐ {cell_text}"
                
            row_data[f"Pick {pk+1}"] = cell_text
        board_display.append(row_data)

    df_board = pd.DataFrame(board_display, index=[f"Round {r+1}" for r in range(16)])
    
    # Display the grid
    st.dataframe(df_board, use_container_width=True, height=600)
    
    st.markdown("""
    **Pro Tip:** To lock in Brock Bowers at 5.10 and Drake Maye at 11.10, open the **Assign Players to Slots** sidebar on the left, search for slot `5.10 (Something Something Drake Maye)`, choose Brock Bowers, and click Assign. Repeat for 11.10 and Drake Maye.
    """)

with tab2:
    st.subheader("Available Players (Sorted by Value Over Replacement)")
    st.dataframe(available_df[['Player', 'Position', 'Team', 'Tier', 'VOR', 'ADP']], use_container_width=True, height=600)