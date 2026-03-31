"""Enhanced Transfermarkt Analytics - Streamlit Application"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import init_db, get_db
from database.models import League, Club, Player, Match, MatchStatistic, DataSource
from sqlalchemy import func, and_
import os

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="⚽ Transfermarkt Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== STYLING =====
st.markdown("""
    <style>
    .main { padding: 0; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stat-box {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ===== DATABASE INITIALIZATION =====
init_db()

# ===== HELPER FUNCTIONS =====
@st.cache_resource
def get_session():
    return get_db()

def format_market_value(value):
    """Format market value in millions or billions"""
    if value is None or value == 0:
        return "N/A"
    if value >= 1000:
        return f"${value/1000:.1f}B"
    else:
        return f"${value:.1f}M"

def get_data_sources_status(db):
    """Get status of all data sources"""
    sources = db.query(DataSource).all()
    return {s.name: {'status': s.status, 'last_sync': s.last_sync} for s in sources}

# ===== SIDEBAR NAVIGATION =====
st.sidebar.image("https://www.transfermarkt.com/assets/img/logo.png" if False else None, use_column_width=True)

st.sidebar.title("📊 TM Analytics Pro")
st.sidebar.divider()

# Data sources status
db = get_session()
sources_status = get_data_sources_status(db)
if sources_status:
    st.sidebar.subheader("📡 Data Sources")
    for source, status_info in sources_status.items():
        color = "🟢" if status_info['status'] == 'active' else "🔴"
        st.sidebar.write(f"{color} {source.title()}")

st.sidebar.divider()

# Navigation
pages = {
    "🏠 Dashboard": "dashboard",
    "⚽ Clubs": "clubs",
    "👤 Players": "players",
    "🏟️ Matches": "matches",
    "📊 Match Analysis": "analysis",
    "📈 Statistics": "statistics",
    "⚙️ Settings": "settings"
}

current_page = st.sidebar.radio("Navigation", list(pages.keys()))
page_key = pages[current_page]

# Scraper button
st.sidebar.divider()
if st.sidebar.button("🔄 Update Data (Refresh)", use_container_width=True):
    with st.spinner("Updating data from sources... (This may take 10-15 minutes)"):
        try:
            from run_scraper import run_scraper
            run_scraper()
            st.sidebar.success("✅ Data updated successfully!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"❌ Error: {e}")

# ===== PAGE: DASHBOARD =====
if page_key == "dashboard":
    st.title("⚽ General Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    leagues_count = db.query(func.count(League.id)).scalar() or 0
    clubs_count = db.query(func.count(Club.id)).scalar() or 0
    players_count = db.query(func.count(Player.id)).scalar() or 0
    matches_count = db.query(func.count(Match.id)).scalar() or 0
    
    col1.metric("🏆 Leagues", leagues_count)
    col2.metric("⚽ Clubs", clubs_count)
    col3.metric("👥 Players", players_count)
    col4.metric("🎯 Matches", matches_count)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Supported Leagues")
        leagues = db.query(League).all()
        if leagues:
            league_data = []
            for league in leagues:
                clubs = db.query(func.count(Club.id)).filter(Club.league_id == league.id).scalar()
                league_data.append({
                    "League": league.name,
                    "Country": league.country,
                    "Clubs": clubs,
                    "Code": league.code
                })
            df_leagues = pd.DataFrame(league_data)
            st.dataframe(df_leagues, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("💰 Total Market Value by League")
        league_values = db.query(
            League.name,
            func.sum(Club.market_value).label('total_value')
        ).join(Club).group_by(League.name).all()
        
        if league_values:
            df_values = pd.DataFrame(
                [(l[0], l[1] or 0) for l in league_values],
                columns=["League", "Market Value (Millions)"]
            )
            fig = px.bar(df_values, x="League", y="Market Value (Millions)", 
                        color="Market Value (Millions)", colorscale="Viridis")
            st.plotly_chart(fig, use_container_width=True)

# ===== PAGE: CLUBS =====
elif page_key == "clubs":
    st.title("⚽ Clubs")
    
    leagues = db.query(League).all()
    
    if leagues:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_league = st.selectbox(
                "Select League",
                [l.name for l in leagues],
                key="league_selector"
            )
        
        with col2:
            sort_by = st.selectbox("Sort By", ["Market Value", "Name"])
        
        league = db.query(League).filter(League.name == selected_league).first()
        clubs = db.query(Club).filter(Club.league_id == league.id).all()
        
        if clubs:
            clubs_data = []
            for club in clubs:
                players_count = db.query(func.count(Player.id)).filter(Player.club_id == club.id).scalar()
                clubs_data.append({
                    "Club": club.name,
                    "Market Value (M€)": club.market_value or 0,
                    "Players": players_count,
                    "Stadium": club.stadium or "N/A"
                })
            
            df_clubs = pd.DataFrame(clubs_data)
            
            if sort_by == "Market Value":
                df_clubs = df_clubs.sort_values("Market Value (M€)", ascending=False)
            else:
                df_clubs = df_clubs.sort_values("Club")
            
            # Display as table
            st.dataframe(df_clubs, use_container_width=True, hide_index=True)
            
            # Chart
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(df_clubs.head(15), x="Club", y="Market Value (M€)",
                            title="Top 15 Clubs by Market Value",
                            color="Market Value (M€)", colorscale="Blues")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(df_clubs, x="Market Value (M€)", y="Players",
                                title="Market Value vs Number of Players",
                                size="Market Value (M€)", hover_data=["Club"],
                                color="Market Value (M€)", colorscale="Greens")
                st.plotly_chart(fig, use_container_width=True)

# ===== PAGE: PLAYERS =====
elif page_key == "players":
    st.title("👤 Players")
    
    clubs = db.query(Club).order_by(Club.name).all()
    
    if clubs:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_club = st.selectbox(
                "Select Club",
                [c.name for c in clubs],
                key="club_selector"
            )
        
        with col2:
            position_filter = st.selectbox("Position", ["All"] + ["GK", "DEF", "MID", "FWD"])
        
        with col3:
            sort_by = st.selectbox("Sort By", ["Market Value", "Age", "Name"])
        
        club = db.query(Club).filter(Club.name == selected_club).first()
        players = db.query(Player).filter(Player.club_id == club.id).all()
        
        if players:
            players_data = []
            for player in players:
                players_data.append({
                    "Name": player.name,
                    "Position": player.position or "N/A",
                    "Age": player.age or "N/A",
                    "Jersey": player.jersey_number or "N/A",
                    "Market Value (M€)": player.market_value or 0,
                    "Country": player.country or "N/A"
                })
            
            df_players = pd.DataFrame(players_data)
            
            # Filtering
            if position_filter != "All":
                df_players = df_players[df_players["Position"].str.contains(position_filter, case=False, na=False)]
            
            # Sorting
            if sort_by == "Market Value":
                df_players = df_players.sort_values("Market Value (M€)", ascending=False)
            elif sort_by == "Age":
                df_players["Age_num"] = pd.to_numeric(df_players["Age"], errors='coerce')
                df_players = df_players.sort_values("Age_num")
                df_players = df_players.drop("Age_num", axis=1)
            else:
                df_players = df_players.sort_values("Name")
            
            st.dataframe(df_players, use_container_width=True, hide_index=True)
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Players", len(df_players))
            
            with col2:
                avg_value = df_players["Market Value (M€)"].mean()
                st.metric("Avg Market Value", f"€{avg_value:.1f}M")
            
            with col3:
                avg_age = pd.to_numeric(df_players["Age"], errors='coerce').mean()
                st.metric("Avg Age", f"{avg_age:.1f} years")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                position_counts = df_players["Position"].value_counts()
                fig = px.pie(values=position_counts.values, names=position_counts.index,
                            title="Players by Position")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                age_dist = pd.to_numeric(df_players["Age"], errors='coerce')
                fig = px.histogram(age_dist, nbins=10, title="Age Distribution",
                                  labels={"value": "Age", "count": "Number of Players"})
                st.plotly_chart(fig, use_container_width=True)

# ===== PAGE: MATCHES =====
elif page_key == "matches":
    st.title("🏟️ Match Results")
    
    leagues = db.query(League).all()
    
    if leagues:
        selected_league = st.selectbox(
            "Select League",
            [l.name for l in leagues],
            key="match_league_selector"
        )
        
        league = db.query(League).filter(League.name == selected_league).first()
        matches = db.query(Match).filter(Match.league_id == league.id).order_by(Match.match_date.desc()).all()
        
        if matches:
            match_data = []
            for match in matches:
                match_data.append({
                    "Date": match.match_date or "N/A",
                    "Home": match.home_club.name,
                    "Score": f"{match.home_goals or '-'} - {match.away_goals or '-'}",
                    "Away": match.away_club.name,
                    "Status": match.status or "N/A",
                    "Stadium": match.stadium or "N/A"
                })
            
            df_matches = pd.DataFrame(match_data)
            st.dataframe(df_matches, use_container_width=True, hide_index=True)
            
            # Stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Matches", len(df_matches))
            
            with col2:
                finished = df_matches[df_matches["Status"] == "Finished"].shape[0]
                st.metric("Finished", finished)
            
            with col3:
                scheduled = df_matches[df_matches["Status"] == "Scheduled"].shape[0]
                st.metric("Scheduled", scheduled)

# ===== PAGE: MATCH ANALYSIS =====
elif page_key == "analysis":
    st.title("📊 Detailed Match Analysis")
    
    st.info("🔍 Select a match to view detailed statistics from multiple sources")
    
    leagues = db.query(League).all()
    
    if leagues:
        selected_league = st.selectbox(
            "Select League",
            [l.name for l in leagues],
            key="analysis_league_selector"
        )
        
        league = db.query(League).filter(League.name == selected_league).first()
        matches = db.query(Match).filter(
            and_(Match.league_id == league.id, Match.status == 'Finished')
        ).order_by(Match.match_date.desc()).all()
        
        if matches:
            match_options = [f"{m.home_club.name} vs {m.away_club.name} ({m.match_date})" for m in matches]
            selected_match_idx = st.selectbox("Select Match", range(len(match_options)), format_func=lambda x: match_options[x])
            
            selected_match = matches[selected_match_idx]
            
            st.subheader(f"{selected_match.home_club.name} {selected_match.home_goals} - {selected_match.away_goals} {selected_match.away_club.name}")
            
            # Get match statistics
            stats = db.query(MatchStatistic).filter(MatchStatistic.match_id == selected_match.id).all()
            
            if stats:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📊 Data Sources", len(stats))
                
                # Display statistics from each source
                for stat in stats:
                    st.subheader(f"📈 {stat.source.title()} Statistics")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    if stat.home_possession:
                        col1.metric("Home Possession", f"{stat.home_possession}%")
                        col2.metric("Away Possession", f"{stat.away_possession}%")
                    
                    if stat.home_shots_total:
                        col1.metric("Home Shots", stat.home_shots_total)
                        col2.metric("Away Shots", stat.away_shots_total)
                        col3.metric("On Target (Home)", stat.home_shots_on_target or "N/A")
                    
                    if stat.home_passes_total:
                        col1.metric("Home Passes", stat.home_passes_total)
                        col2.metric("Away Passes", stat.away_passes_total)
                        col3.metric("Pass Accuracy (Home)", f"{stat.home_pass_accuracy}%" if stat.home_pass_accuracy else "N/A")
                    
                    # Create comparison chart
                    stat_categories = ['Shots', 'Passes', 'Corners', 'Fouls']
                    home_values = [
                        stat.home_shots_total or 0,
                        stat.home_passes_total or 0 // 100,  # Scale down for visibility
                        stat.home_corners or 0,
                        stat.home_fouls or 0
                    ]
                    away_values = [
                        stat.away_shots_total or 0,
                        stat.away_passes_total or 0 // 100,
                        stat.away_corners or 0,
                        stat.away_fouls or 0
                    ]
                    
                    fig = go.Figure(data=[
                        go.Bar(name=selected_match.home_club.name, x=stat_categories, y=home_values),
                        go.Bar(name=selected_match.away_club.name, x=stat_categories, y=away_values)
                    ])
                    fig.update_layout(barmode='group', title='Match Statistics Comparison')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No detailed statistics available for this match yet. Try updating data.")

# ===== PAGE: STATISTICS =====
elif page_key == "statistics":
    st.title("📈 League Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 League Market Value Distribution")
        league_values = db.query(
            League.name,
            func.sum(Club.market_value).label('total_value')
        ).join(Club).group_by(League.name).all()
        
        if league_values:
            df_values = pd.DataFrame(
                [(l[0], l[1] or 0) for l in league_values],
                columns=["League", "Market Value"]
            )
            fig = px.pie(df_values, values="Market Value", names="League", title="Market Value Share")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Average Player Market Value by League")
        player_values = db.query(
            League.name,
            func.avg(Player.market_value).label('avg_value'),
            func.count(Player.id).label('player_count')
        ).join(Club).join(League).group_by(League.name).all()
        
        if player_values:
            df_player_values = pd.DataFrame(
                [(p[0], p[1] or 0) for p in player_values],
                columns=["League", "Avg Player Value (M€)"]
            )
            fig = px.bar(df_player_values, x="League", y="Avg Player Value (M€)",
                        color="Avg Player Value (M€)", colorscale="Sunset")
            st.plotly_chart(fig, use_container_width=True)

# ===== PAGE: SETTINGS =====
elif page_key == "settings":
    st.title("⚙️ Settings & Data Management")
    
    st.subheader("📊 Data Source Status")
    sources = db.query(DataSource).all()
    
    if sources:
        source_data = []
        for source in sources:
            source_data.append({
                "Source": source.name.title(),
                "Status": source.status,
                "Last Sync": source.last_sync,
                "Error": source.error_message or "None"
            })
        
        df_sources = pd.DataFrame(source_data)
        st.dataframe(df_sources, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("🗑️ Database Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reset Database"):
            if st.confirm("Are you sure? This will delete all data."):
                try:
                    from database import reset_db
                    reset_db()
                    st.success("Database reset successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        st.button("📊 View Database Stats", disabled=True)
    
    with col3:
        st.button("⬇️ Export Data", disabled=True)

# ===== FOOTER =====
st.divider()
st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
        <p>⚽ Transfermarkt Analytics Pro | Data from Transfermarkt, SofaScore, FotMob</p>
        <p>Last updated: 2024 | © All rights reserved</p>
    </div>
""", unsafe_allow_html=True)

db.close()
