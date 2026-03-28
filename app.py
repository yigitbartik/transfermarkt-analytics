import streamlit as st
import pandas as pd
from database.db import init_db, SessionLocal
from database.models import League, Club, Player, Match
from sqlalchemy import func
import plotly.express as px
import os

# --- RUN_SCRAPER İÇERİ AKTARMA ---
run_scraper_func = None
if os.path.exists("run_scraper.py"):
    try:
        import run_scraper
        run_scraper_func = run_scraper.run_scraper
    except Exception as e:
        st.sidebar.error(f"Scraper dosyası yüklendi ama çalıştırılamıyor: {e}")
else:
    st.sidebar.warning("⚠️ run_scraper.py dosyası ana dizinde bulunamadı.")

# Veritabanını hazırla
init_db()

# Sayfa ayarları
st.set_page_config(page_title="Transfermarkt Analytics 2026", layout="wide")

# Kenar Çubuğu
st.sidebar.title("📊 TM Analytics")
page = st.sidebar.radio("Navigasyon", ["Dashboard", "Clubs", "Players", "Matches", "Statistics"])

# --- VERİ ÇEKME BUTONU (Key parametresi eklendi!) ---
st.sidebar.divider()
# 'key="scraper_btn_unique"' ekleyerek çakışmayı önledik
if st.sidebar.button("🔄 Verileri Çek / Güncelle", use_container_width=True, key="scraper_btn_unique"):
    if run_scraper_func is not None:
        with st.spinner("Transfermarkt verileri çekiliyor... Lütfen bekleyin."):
            try:
                run_scraper_func()
                st.sidebar.success("Veriler başarıyla güncellendi!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Veri çekilirken hata oluştu: {e}")
    else:
        st.sidebar.error("Hata: run_scraper.py bulunamadı!")

# Veritabanı Yardımcı Fonksiyonu
def get_db():
    return SessionLocal()

# --- SAYFALAR ---

if page == "Dashboard":
    st.title("⚽ Football Analytics Dashboard")
    db = get_db()
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Leagues", db.query(func.count(League.id)).scalar() or 0)
        with col2:
            st.metric("Total Clubs", db.query(func.count(Club.id)).scalar() or 0)
        with col3:
            st.metric("Total Players", db.query(func.count(Player.id)).scalar() or 0)
        with col4:
            st.metric("Total Matches", db.query(func.count(Match.id)).scalar() or 0)
        
        st.divider()
        st.subheader("📋 Aktif Ligler")
        leagues = db.query(League).all()
        if leagues:
            df_leagues = pd.DataFrame([(l.code, l.name, l.country) for l in leagues], columns=["Kod", "Lig Adı", "Ülke"])
            st.dataframe(df_leagues, use_container_width=True)
        else:
            st.info("Veritabanı boş. Lütfen soldaki butondan verileri çekin.")
    finally:
        db.close()

elif page == "Clubs":
    st.title("⚽ Kulüp Analizi")
    db = get_db()
    try:
        leagues = db.query(League).all()
        if leagues:
            selected_league = st.selectbox("Lig Seçin", [l.name for l in leagues])
            league = db.query(League).filter(League.name == selected_league).first()
            clubs = db.query(Club).filter(Club.league_id == league.id).all()
            
            if clubs:
                club_list = []
                for c in clubs:
                    club_list.append({
                        "Kulüp Adı": c.name,
                        "Değer (M€)": c.market_value,
                        "Oyuncu Sayısı": len(c.players) if c.players else 0,
                        "TM ID": c.transfermarkt_id
                    })
                st.dataframe(pd.DataFrame(club_list), use_container_width=True)
    finally:
        db.close()

elif page == "Players":
    st.title("👤 Oyuncu Kadroları")
    db = get_db()
    try:
        clubs = db.query(Club).order_by(Club.name).all()
        if clubs:
            selected_club = st.selectbox("Kulüp Seçin", [c.name for c in clubs])
            club = db.query(Club).filter(Club.name == selected_club).first()
            players = db.query(Player).filter(Player.club_id == club.id).all()
            
            if players:
                player_list = [{
                    "Ad": p.name,
                    "Pozisyon": p.position or "Bilinmiyor",
                    "Yaş": p.age or "N/A",
                    "Değer (M€)": p.market_value
                } for p in players]
                st.dataframe(pd.DataFrame(player_list), use_container_width=True)
    finally:
        db.close()

elif page == "Matches":
    st.title("🏟️ Fikstür ve Sonuçlar")
    db = get_db()
    try:
        leagues = db.query(League).all()
        if leagues:
            selected_league = st.selectbox("Lig Seçin", [l.name for l in leagues])
            league = db.query(League).filter(League.name == selected_league).first()
            matches = db.query(Match).filter(Match.league_id == league.id).all()
            
            if matches:
                match_list = [{
                    "Ev Sahibi": m.home_club.name if m.home_club else "N/A",
                    "Deplasman": m.away_club.name if m.away_club else "N/A",
                    "Skor": f"{m.home_goals} - {m.away_goals}" if m.home_goals is not None else "Oynanmadı",
                    "Durum": m.status
                } for m in matches]
                st.dataframe(pd.DataFrame(match_list), use_container_width=True)
    finally:
        db.close()

elif page == "Statistics":
    st.title("📈 İstatistiksel Özet")
    db = get_db()
    try:
        data = db.query(League.name, func.sum(Club.market_value)).join(Club).group_by(League.name).all()
        if data:
            df = pd.DataFrame(data, columns=["Lig", "Toplam Değer (M€)"])
            fig = px.pie(df, values="Toplam Değer (M€)", names="Lig", title="Liglerin Ekonomik Dağılımı")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("İstatistik oluşturmak için yeterli veri yok.")
    finally:
        db.close()