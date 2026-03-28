import streamlit as st
import pandas as pd
from database.db import init_db, SessionLocal
from database.models import League, Club, Player, Match
from sqlalchemy import func
import plotly.express as px

# Veri çekme fonksiyonunu içeri aktarıyoruz. 
try:
    from run_scraper import run_scraper
except ImportError:
    run_scraper = None

init_db()

st.set_page_config(page_title="Transfermarkt Analytics", layout="wide")

st.sidebar.title("📊 Transfermarkt Analytics")
page = st.sidebar.radio("Navigation", ["Dashboard", "Clubs", "Players", "Matches", "Statistics"])

# --- YENİ EKLENEN VERİ ÇEKME BUTONU ---
st.sidebar.divider()
if st.sidebar.button("🔄 Verileri Çek / Güncelle", use_container_width=True):
    if run_scraper is not None:
        with st.spinner("Transfermarkt'tan veriler çekiliyor... (Bu işlem uzun sürebilir)"):
            try:
                run_scraper()  
                st.sidebar.success("Veriler başarıyla çekildi ve veritabanına eklendi!")
                st.rerun() 
            except Exception as e:
                st.sidebar.error(f"Veri çekilirken bir hata oluştu: {e}")
    else:
        st.sidebar.error("Veri çekme dosyası (run_scraper.py) bulunamadı! Lütfen dosya adını kontrol edin.")
# --------------------------------------

def get_db():
    return SessionLocal()

if page == "Dashboard":
    st.title("⚽ Football Analytics Dashboard")
    
    db = get_db()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        leagues_count = db.query(func.count(League.id)).scalar()
        st.metric("Total Leagues", leagues_count or 0)
    
    with col2:
        clubs_count = db.query(func.count(Club.id)).scalar()
        st.metric("Total Clubs", clubs_count or 0)
    
    with col3:
        players_count = db.query(func.count(Player.id)).scalar()
        st.metric("Total Players", players_count or 0)
    
    with col4:
        matches_count = db.query(func.count(Match.id)).scalar()
        st.metric("Total Matches", matches_count or 0)
    
    st.divider()
    
    st.subheader("📋 Supported Leagues")
    leagues = db.query(League).all()
    if leagues:
        league_data = [(l.code, l.name, l.country) for l in leagues]
        df_leagues = pd.DataFrame(league_data, columns=["Code", "League Name", "Country"])
        st.dataframe(df_leagues, width="stretch")
    else:
        st.info("No leagues found. Please run the scraper from the sidebar first.")
    
    db.close()

elif page == "Clubs":
    st.title("⚽ Clubs")
    
    db = get_db()
    
    leagues = db.query(League).all()
    league_names = [l.name for l in leagues]
    
    if league_names:
        selected_league = st.selectbox("Select League", league_names)
        
        if selected_league:
            league = db.query(League).filter(League.name == selected_league).first()
            clubs = db.query(Club).filter(Club.league_id == league.id).all()
            
            if clubs:
                club_data = []
                for club in clubs:
                    club_data.append({
                        "Name": club.name,
                        "Country": club.country or "N/A",
                        "Stadium": club.stadium or "N/A",
                        "Market Value": club.market_value or 0,
                        "Players": len(club.players) if club.players else 0
                    })
                
                df_clubs = pd.DataFrame(club_data)
                st.dataframe(df_clubs, width="stretch")
            else:
                st.info("No clubs found for this league.")
    else:
        st.info("No leagues found.")
    
    db.close()

elif page == "Players":
    st.title("👤 Players")
    
    db = get_db()
    
    clubs = db.query(Club).all()
    club_names = [c.name for c in clubs]
    
    if club_names:
        selected_club = st.selectbox("Select Club", club_names)
        
        if selected_club:
            club = db.query(Club).filter(Club.name == selected_club).first()
            players = db.query(Player).filter(Player.club_id == club.id).all()
            
            if players:
                player_data = []
                for player in players:
                    player_data.append({
                        "Name": player.name,
                        "Position": player.position or "N/A",
                        "Age": player.age or 0,
                        "Jersey": player.jersey_number or 0,
                        "Market Value": player.market_value or 0,
                        "Height": player.height or "N/A"
                    })
                
                df_players = pd.DataFrame(player_data)
                st.dataframe(df_players, width="stretch")
            else:
                st.info("No players found for this club.")
    else:
        st.info("No clubs found.")
    
    db.close()

elif page == "Matches":
    st.title("🏟️ Matches")
    
    db = get_db()
    
    leagues = db.query(League).all()
    league_names = [l.name for l in leagues]
    
    if league_names:
        selected_league = st.selectbox("Select League", league_names)
        
        if selected_league:
            league = db.query(League).filter(League.name == selected_league).first()
            matches = db.query(Match).filter(Match.league_id == league.id).all()
            
            if matches:
                match_data = []
                for match in matches:
                    match_data.append({
                        "Date": match.match_date or "N/A",
                        "Time": match.match_time or "N/A",
                        "Home": match.home_club.name if match.home_club else "N/A",
                        "Away": match.away_club.name if match.away_club else "N/A",
                        "Score": f"{match.home_goals or '-'} vs {match.away_goals or '-'}",
                        "Status": match.status or "N/A",
                        "Attendance": match.attendance or 0
                    })
                
                df_matches = pd.DataFrame(match_data)
                st.dataframe(df_matches, width="stretch")
            else:
                st.info("No matches found for this league.")
    else:
        st.info("No leagues found.")
    
    db.close()

elif page == "Statistics":
    st.title("📈 Statistics")
    
    db = get_db()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Clubs by League")
        clubs_by_league = db.query(League.name, func.count(Club.id).label("count"))\
            .select_from(League)\
            .join(Club)\
            .group_by(League.name)\
            .all()
            
        if clubs_by_league:
            df = pd.DataFrame(clubs_by_league, columns=["League", "Count"])
            fig = px.bar(df, x="League", y="Count", title="Number of Clubs per League")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    
    with col2:
        st.subheader("Players by League")
        players_by_league = db.query(League.name, func.count(Player.id).label("count"))\
            .select_from(League)\
            .join(Club)\
            .join(Player)\
            .group_by(League.name)\
            .all()
            
        if players_by_league:
            df = pd.DataFrame(players_by_league, columns=["League", "Count"])
            fig = px.pie(df, names="League", values="Count", title="Player Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    
    db.close()