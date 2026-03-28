import streamlit as st
import pandas as pd
from database.db import init_db, SessionLocal
from database.models import League, Club, Player, Match
from sqlalchemy import func
import plotly.express as px
import os

# Veritabanını başlat
init_db()

st.set_page_config(page_title="Transfermarkt Analytics 2026", layout="wide")

# --- SCRAPER MODÜLÜNÜ GÜVENLİ YÜKLEME ---
run_scraper_func = None
scraper_status = "Bilinmiyor"
current_files = os.listdir(".")

if "run_scraper.py" in current_files:
    try:
        import run_scraper
        run_scraper_func = run_scraper.run_scraper
        scraper_status = "Hazır ✅"
    except Exception as e:
        scraper_status = f"Hata ❌ ({e})"
else:
    scraper_status = "Dosya Bulunamadı ⚠️"

# --- SIDEBAR (KENAR ÇUBUĞU) ---
st.sidebar.title("📊 TM Analytics")
st.sidebar.info(f"Scraper: {scraper_status}")

# Hata ayıklama: Dosya yoksa listeyi göster
if "run_scraper.py" not in current_files:
    st.sidebar.write("Dizin Dosyaları:", current_files)

page = st.sidebar.radio("Navigasyon", ["Dashboard", "Clubs", "Players", "Matches", "Statistics"])

# --- VERİ ÇEKME BUTONU (Benzersiz Key eklendi) ---
st.sidebar.divider()
if st.sidebar.button("🔄 Verileri Çek / Güncelle", use_container_width=True, key="main_scraper_btn_2026"):
    if run_scraper_func is not None:
        with st.spinner("Transfermarkt verileri çekiliyor... (5-10 dk sürebilir)"):
            try:
                run_scraper_func()
                st.sidebar.success("Güncelleme Başarılı!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Hata oluştu: {e}")
    else:
        st.sidebar.error("run_scraper.py dosyasına ulaşılamıyor!")

def get_db():
    return SessionLocal()

# --- SAYFALAR ---

if page == "Dashboard":
    st.title("⚽ Football Analytics Dashboard")
    db = get_db()
    try:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Lig Sayısı", db.query(func.count(League.id)).scalar() or 0)
        with col2:
            st.metric("Kulüp Sayısı", db.query(func.count(Club.id)).scalar() or 0)
        with col3:
            st.metric("Oyuncu Sayısı", db.query(func.count(Player.id)).scalar() or 0)
        with col4:
            st.metric("Maç Sayısı", db.query(func.count(Match.id)).scalar() or 0)
        
        st.divider()
        st.subheader("📋 Sistemdeki Ligler")
        leagues = db.query(League).all()
        if leagues:
            df_leagues = pd.DataFrame([(l.code, l.name, l.country) for l in leagues], columns=["Kod", "Lig", "Ülke"])
            st.dataframe(df_leagues, use_container_width=True)
        else:
            st.info("Henüz veri yok.")
    finally:
        db.close()

elif page == "Clubs":
    st.title("⚽ Kulüpler")
    db = get_db()
    try:
        leagues = db.query(League).all()
        if leagues:
            # ÇAKIŞMAYI ÖNLEYEN KEY: 'clubs_league_select'
            selected_league = st.selectbox("Lig Seçin", [l.name for l in leagues], key="clubs_league_select")
            league = db.query(League).filter(League.name == selected_league).first()
            clubs = db.query(Club).filter(Club.league_id == league.id).all()
            if clubs:
                df_clubs = pd.DataFrame([{
                    "Kulüp": c.name,
                    "Değer (M€)": f"{c.market_value:,.2f}",
                    "Kadro": len(c.players)
                } for c in clubs])
                st.dataframe(df_clubs, use_container_width=True)
    finally:
        db.close()

elif page == "Players":
    st.title("👤 Oyuncular")
    db = get_db()
    try:
        clubs = db.query(Club).order_by(Club.name).all()
        if clubs:
            # ÇAKIŞMAYI ÖNLEYEN KEY: 'players_club_select'
            selected_club = st.selectbox("Kulüp Seçin", [c.name for c in clubs], key="players_club_select")
            club = db.query(Club).filter(Club.name == selected_club).first()
            players = db.query(Player).filter(Player.club_id == club.id).all()
            if players:
                df_p = pd.DataFrame([{
                    "Ad": p.name,
                    "Mevki": p.position,
                    "Yaş": p.age,
                    "Değer (M€)": f"{p.market_value:,.2f}"
                } for p in players])
                st.dataframe(df_p, use_container_width=True)
    finally:
        db.close()

elif page == "Matches":
    st.title("🏟️ Maçlar")
    db = get_db()
    try:
        leagues = db.query(League).all()
        if leagues:
            # ÇAKIŞMAYI ÖNLEYEN KEY: 'matches_league_select'
            selected_league = st.selectbox("Lig Seçin", [l.name for l in leagues], key="matches_league_select")
            league = db.query(League).filter(League.name == selected_league).first()
            matches = db.query(Match).filter(Match.league_id == league.id).all()
            if matches:
                df_m = pd.DataFrame([{
                    "Ev Sahibi": m.home_club.name if m.home_club else "N/A",
                    "Deplasman": m.away_club.name if m.away_club else "N/A",
                    "Skor": f"{m.home_goals} - {m.away_goals}" if m.home_goals is not None else "Tarih Bekleniyor",
                    "Durum": m.status
                } for m in matches])
                st.dataframe(df_m, use_container_width=True)
    finally:
        db.close()

elif page == "Statistics":
    st.title("📈 İstatistikler")
    db = get_db()
    try:
        data = db.query(League.name, func.sum(Club.market_value)).join(Club).group_by(League.name).all()
        if data:
            df = pd.DataFrame(data, columns=["Lig", "Değer"])
            st.plotly_chart(px.pie(df, values="Değer", names="Lig", title="Liglerin Toplam Piyasa Değeri"), use_container_width=True)
        else:
            st.warning("Veri çekilmeden analiz yapılamaz.")
    finally:
        db.close()