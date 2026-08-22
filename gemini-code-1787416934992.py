@st.cache_data
def load_data():
    df = pd.read_csv('fantasy_football_rankings.csv')
    df = df[['Player', 'Position', 'Team', 'Tier', 'Consensus', 'ADP']].copy()
    
    # 1. Calculate Positional Rank
    df['Pos_Rank'] = df.groupby('Position')['Consensus'].rank(method='min')
    
    # 2. Assign Estimated Fantasy Points (Exponential decay based on Positional Rank)
    # This simulates the steep drop-off at QB and the flatter curve at WR
    def estimate_points(row):
        pos = row['Position']
        rank = row['Pos_Rank']
        
        # Base points by position for the #1 player
        base = {'QB': 380, 'RB': 300, 'WR': 280, 'TE': 220, 'K': 140, 'DST': 130}
        
        # Decay rates: QBs drop fast, WRs drop slowly (deep position)
        decay = {'QB': 0.025, 'RB': 0.020, 'WR': 0.015, 'TE': 0.030, 'K': 0.015, 'DST': 0.015}
        
        import math
        if pos in base:
            return base[pos] * math.exp(-decay[pos] * (rank - 1))
        return 0
        
    df['Est_Pts'] = df.apply(estimate_points, axis=1)
    
    # 3. Determine Replacement Level Points based on 12-team 2QB/2Flex
    baselines = {'QB': 28, 'RB': 48, 'WR': 60, 'TE': 16, 'K': 12, 'DST': 12}
    
    rep_pts = {}
    for pos, base_rank in baselines.items():
        pos_df = df[df['Position'] == pos]
        if len(pos_df) >= base_rank:
            rep_pts[pos] = pos_df[pos_df['Pos_Rank'] == base_rank].iloc[0]['Est_Pts']
        else:
            rep_pts[pos] = pos_df['Est_Pts'].min() if not pos_df.empty else 0
            
    # 4. Calculate True VOR (Estimated Points - Replacement Level Points)
    df['VOR'] = df.apply(lambda row: round(row['Est_Pts'] - rep_pts.get(row['Position'], 0), 1), axis=1)
    
    # Sort by VOR descending to prioritize scarce positions
    return df.sort_values('VOR', ascending=False).reset_index(drop=True)