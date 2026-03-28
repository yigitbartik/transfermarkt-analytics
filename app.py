import streamlit as st
import pandas as pd
from database.db import init_db, SessionLocal
from database.models import League, Club, Player, Match
from sqlalchemy import func
import plotly.express as px
import os

# Veritabanı ve Sayfa Yapılandırması
init_db()
st.set_page_config(page_title="Transfermarkt Analytics", layout="wide")

# Scraper Import Kontrolü
run_scraper_func = None
if os.path.exists("run_scraper.py"):
    try:
        import run_scraper
        run_scraper_func = run_scraper.run_scraper
    except Exception as e:
        st.sidebar.error(f"Scraper yuklenemedi: {e}")

# Sidebar Navigasyon
st.sidebar.title("📊 TM Analytics")
page = st.sidebar.radio("Sayfalar", ["Dashboard", "Clubs", "Players", "Matches", "Statistics"])

# Veri Güncelleme Butonu (Unique Key ile)
st.sidebar.divider()
if st.sidebar.button("🔄 Verileri Güncelle", use_container_width=True, key="btn_global_scraper"):
    if run_scraper_func:
        with st.spinner("Veriler Transfermarkt'tan alınıyor... (Bu işlem 10-15 dk sürebilir)"):
            try:
                run_scraper_func()
                st.sidebar.success("Güncellendi!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Hata: {e}")
    else:
        st.sidebar.error("run_scraper.py bulunamadı!")

def get_db():
    return SessionLocal()

# --- DASHBOARD ---
if page == "Dashboard":
    st.title("⚽ Genel Bakış")
    db = get_db()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ligler", db.query(func.count(League.id)).scalar() or 0)
    c2.metric("Kulüpler", db.query(func.count(Club.id)).scalar() or 0)
    c3.metric("Oyuncular", db.query(func.count(Player.id)).scalar() or 0)
    c4.metric("Maçlar", db.query(func.count(Match.id)).scalar() or 0)
    
    st.divider()
    leagues = db.query(League).all()
    if leagues:
        df = pd.DataFrame([(l.name, l.country) for l in leagues], columns=["Lig", "Ülke"])
        st.subheader("📋 Desteklenen Ligler")
        st.dataframe(df, use_container_width=True)
    db.close()

# --- CLUBS ---
elif page == "Clubs":
    st.title("⚽ Kulüpler")
    db = get_db()
    leagues = db.query(League).all()
    if leagues:
        sel_league = st.selectbox("Lig Seç", [l.name for l in leagues], key="sel_club_league")
        league = db.query(League).filter(League.name == sel_league).first()
        clubs = db.query(Club).filter(Club.league_id == league.id).all()
        if clubs:
            df = pd.DataFrame([{"Kulüp": c.name, "Değer (M€)": c.market_value} for c in clubs])
            st.dataframe(df.sort_values("Değer (M€)", ascending=False), use_container_width=True)
    db.close()

# --- PLAYERS ---
elif page == "Players":
    st.title("👤 Oyuncular")
    db = get_db()
    clubs = db.query(Club).order_by(Club.name).all()
    if clubs:
        sel_club = st.selectbox("Kulüp Seç", [c.name for c in clubs], key="sel_player_club")
        club = db.query(Club).filter(Club.name == sel_club).first()
        players = db.query(Player).filter(Player.club_id == club.id).all()
        if players:
            df = pd.DataFrame([{"Ad": p.name, "Mevki": p.position, "Yaş": p.age, "Değer (M€)": p.market_value} for p in players])
            st.dataframe(df, use_container_width=True)
    db.close()

# --- MATCHES ---
elif page == "Matches":
    st.title("🏟️ Maç Sonuçları")
    db = get_db()
    leagues = db.query(League).all()
    if leagues:
        sel_league = st.selectbox("Lig Seç", [l.name for l in leagues], key="sel_match_league")
        league = db.query(League).filter(League.name == sel_league).first()
        matches = db.query(Match).filter(Match.league_id == league.id).all()
        if matches:
            df = pd.DataFrame([{
                "Ev": m.home_club.name, "Skor": f"{m.home_goals}-{m.away_goals}", "Deplasman": m.away_club.name
            } for m in matches])
            st.table(df)
    db.close()

# --- STATISTICS ---
elif page == "Statistics":
    st.title("📈 İstatistikler")
    db = get_db()
    data = db.query(League.name, func.sum(Club.market_value)).join(Club).group_by(League.name).all()
    if data:
        df = pd.DataFrame(data, columns=["Lig", "Değer"])
        fig = px.pie(df, values="Değer", names="Lig", title="Lig Değer Dağılımı")
        st.plotly_chart(fig, use_container_width=True)
    db.close()