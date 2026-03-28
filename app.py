import streamlit as st
import pandas as pd
from database.db import init_db, SessionLocal
from database.models import League, Club, Player, Match
from sqlalchemy import func
import plotly.express as px
import os
import sys

# Veritabanını başlat
init_db()

st.set_page_config(page_title="Transfermarkt Analytics 2026", layout="wide")

# --- SCRAPER YÜKLEME MANTIĞI ---
run_scraper_func = None
scraper_status = "Bilinmiyor"

# Dosya sistemini kontrol et (Hata ayıklama için)
current_dir_files = os.listdir(".")

if "run_scraper.py" in current_dir_files:
    try:
        # Dinamik olarak import etmeyi dene
        import run_scraper
        run_scraper_func = run_scraper.run_scraper
        scraper_status = "Hazır ✅"
    except Exception as e:
        scraper_status = f"Yükleme Hatası ❌ ({e})"
else:
    scraper_status = "Dosya Bulunamadı ⚠️"

# Sidebar
st.sidebar.title("📊 TM Analytics")
st.sidebar.info(f"Scraper Durumu: {scraper_status}")

# Eğer dosya bulunamadıysa kullanıcıya mevcut dosyaları göster (Sadece hata ayıklama için)
if "run_scraper.py" not in current_dir_files:
    st.sidebar.write("Klasördeki Dosyalar:", current_dir_files)

page = st.sidebar.radio("Navigasyon", ["Dashboard", "Clubs", "Players", "Matches", "Statistics"])

# --- VERİ ÇEKME BUTONU ---
st.sidebar.divider()
if st.sidebar.button("🔄 Verileri Çek / Güncelle", use_container_width=True, key="unique_scraper_button_2026"):
    if run_scraper_func is not None:
        with st.spinner("Veriler çekiliyor... Lütfen sayfayı kapatmayın."):
            try:
                run_scraper_func()
                st.sidebar.success("Güncelleme Başarılı!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Çalıştırma sırasında hata: {e}")
    else:
        st.sidebar.error(f"Hata: run_scraper.py erişilebilir değil. Durum: {scraper_status}")

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
            st.info("Veritabanı şu an boş.")
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
                df_clubs = pd.DataFrame([{
                    "Kulüp Adı": c.name,
                    "Piyasa Değeri (M€)": f"{c.market_value:,.2f}",
                    "Oyuncu Sayısı": len(c.players),
                    "TM ID": c.transfermarkt_id
                } for c in clubs])
                st.dataframe(df_clubs, use_container_width=True)
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
                df_p = pd.DataFrame([{
                    "Ad": p.name,
                    "Pozisyon": p.position,
                    "Yaş": p.age,
                    "Değer (M€)": f"{p.market_value:,.2f}"
                } for p in players])
                st.dataframe(df_p, use_container_width=True)
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
                df_m = pd.DataFrame([{
                    "Ev Sahibi": m.home_club.name if m.home_club else "N/A",
                    "Deplasman": m.away_club.name if m.away_club else "N/A",
                    "Skor": f"{m.home_goals} - {m.away_goals}" if m.home_goals is not None else "Oynanmadı",
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
            st.plotly_chart(px.pie(df, values="Değer", names="Lig", title="Lig Değer Dağılımı"), use_container_width=True)
    finally:
        db.close()