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
    page_title="⚽ TM Analytics Pro",
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
    /* Tablo resimlerini yuvarlama */
    img { border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# ===== DATABASE INITIALIZATION =====
init_db()

# ===== HELPER FUNCTIONS =====
@st.cache_resource
def get_session():
    return get_db()

def format_market_value(value):
    if value is None or value == 0: return "N/A"
    return f"€{value:.1f}M" if value < 1000 else f"€{value/1000:.1f}B"

def get_data_sources_status(db):
    try:
        sources = db.query(DataSource).all()
        return {s.name: {'status': s.status, 'last_sync': s.last_sync} for s in sources}
    except: return {}

# ===== SIDEBAR NAVIGATION =====
db = get_session()
logo_url = "https://www.transfermarkt.com/assets/img/logo.png"
st.sidebar.image(logo_url, width=200)
st.sidebar.title("📊 TM Analytics Pro")

sources_status = get_data_sources_status(db)
if sources_status:
    st.sidebar.subheader("📡 Data Sources")
    for source, info in sources_status.items():
        color = "🟢" if info['status'] == 'active' else "🔴"
        st.sidebar.write(f"{color} {source.title()}")

st.sidebar.divider()
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

st.sidebar.divider()
if st.sidebar.button("🔄 Update Data (Refresh)", use_container_width=True):
    with st.spinner("Updating data..."):
        try:
            from run_scraper import run_scraper
            run_scraper()
            st.sidebar.success("✅ Updated!")
            st.rerun()
        except Exception as e: st.sidebar.error(f"❌ Error: {e}")

# ===== PAGE: DASHBOARD =====
if page_key == "dashboard":
    st.title("⚽ General Overview")
    cols = st.columns(4)
    cols[0].metric("🏆 Leagues", db.query(func.count(League.id)).scalar() or 0)
    cols[1].metric("⚽ Clubs", db.query(func.count(Club.id)).scalar() or 0)
    cols[2].metric("👥 Players", db.query(func.count(Player.id)).scalar() or 0)
    cols[3].metric("🎯 Matches", db.query(func.count(Match.id)).scalar() or 0)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Supported Leagues")
        leagues = db.query(League).all()
        if leagues:
            df_l = pd.DataFrame([{
                "League": l.name, "Country": l.country, 
                "Clubs": db.query(func.count(Club.id)).filter(Club.league_id == l.id).scalar()
            } for l in leagues])
            st.dataframe(df_l, use_container_width=True, hide_index=True)

# ===== PAGE: CLUBS =====
elif page_key == "clubs":
    st.title("⚽ Clubs")
    leagues = db.query(League).all()
    if leagues:
        c1, c2 = st.columns([2, 1])
        sel_league = c1.selectbox("Select League", [l.name for l in leagues])
        sort_by = c2.selectbox("Sort By", ["Market Value", "Name"])
        
        league = db.query(League).filter(League.name == sel_league).first()
        clubs = db.query(Club).filter(Club.league_id == league.id).all()
        
        if clubs:
            df_clubs = pd.DataFrame([{
                "Logo": club.logo_url, # Veritabanında logo_url olduğunu varsayıyoruz
                "Club": club.name,
                "Market Value (M€)": club.market_value or 0,
                "Stadium": club.stadium or "N/A"
            } for club in clubs])
            
            df_clubs = df_clubs.sort_values("Market Value (M€)" if sort_by=="Market Value" else "Club", ascending=(sort_by=="Name"))
            
            st.dataframe(
                df_clubs,
                column_config={"Logo": st.column_config.ImageColumn("Badge")},
                use_container_width=True, hide_index=True
            )

# ===== PAGE: PLAYERS =====
elif page_key == "players":
    st.title("👤 Players")
    clubs = db.query(Club).order_by(Club.name).all()
    if clubs:
        c1, c2, c3 = st.columns([2, 1, 1])
        sel_club = c1.selectbox("Select Club", [c.name for c in clubs])
        pos_filter = c2.selectbox("Position", ["All", "GK", "DEF", "MID", "FWD"])
        sort_by = c3.selectbox("Sort By", ["Market Value", "Age", "Name"])
        
        club = db.query(Club).filter(Club.name == sel_club).first()
        players = db.query(Player).filter(Player.club_id == club.id).all()
        
        if players:
            df_p = pd.DataFrame([{
                "Photo": p.photo_url,
                "Name": p.name,
                "Position": p.position or "N/A",
                "Age": p.age or "N/A",
                "Value (M€)": p.market_value or 0,
                "Country": p.country
            } for p in players])
            
            if pos_filter != "All":
                df_p = df_p[df_p["Position"].str.contains(pos_filter, case=False, na=False)]
            
            st.dataframe(
                df_p,
                column_config={"Photo": st.column_config.ImageColumn("👤")},
                use_container_width=True, hide_index=True
            )

# ===== PAGE: MATCH ANALYSIS =====
elif page_key == "analysis":
    st.title("📊 Match Analysis")
    leagues = db.query(League).all()
    if leagues:
        sel_l = st.selectbox("Select League", [l.name for l in leagues], key="an_l")
        league = db.query(League).filter(League.name == sel_l).first()
        matches = db.query(Match).filter(and_(Match.league_id == league.id, Match.status == 'Finished')).all()
        
        if matches:
            m_opts = [f"{m.home_club.name} {m.home_goals}-{m.away_goals} {m.away_club.name}" for m in matches]
            sel_m_idx = st.selectbox("Select Match", range(len(m_opts)), format_func=lambda x: m_opts[x])
            match = matches[sel_m_idx]
            
            # Gelişmiş İstatistik Gösterimi
            stats = db.query(MatchStatistic).filter(MatchStatistic.match_id == match.id).all()
            if stats:
                for s in stats:
                    st.subheader(f"Source: {s.source.name.upper()}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Possession", f"{s.home_possession}%", f"{s.away_possession}%", delta_color="off")
                    c2.metric("Total Shots", s.home_shots_total, s.away_shots_total)
                    c3.metric("Pass Accuracy", f"{s.home_pass_accuracy}%")
            else:
                st.warning("Eşleşmiş WhoScored/FotMob verisi bulunamadı.")

# ===== FOOTER =====
st.divider()
st.markdown("<div style='text-align: center; color: gray;'>⚽ TM Analytics Pro | 2026</div>", unsafe_allow_html=True)

try: db.close()
except: pass