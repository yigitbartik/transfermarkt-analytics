import streamlit as st
import pandas as pd
from database.db import init_db, SessionLocal
from database.models import League, Club, Player, Match
from sqlalchemy import func
import plotly.express as px
import importlib.util
import os

# --- RUN_SCRAPER İÇERİ AKTARMA (Gelişmiş Hata Yönetimi) ---
# Dosya var mı ve import edilebiliyor mu kontrol ediyoruz
run_scraper_func = None
if os.path.exists("run_scraper.py"):
    try:
        import run_scraper
        run_scraper_func = run_scraper.run_scraper
    except Exception as e:
        # Import sırasında hata oluşursa (içindeki kütüphaneler eksikse vb.)
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

# --- VERİ ÇEKME BUTONU ---
st.sidebar.divider()
if st.sidebar.button("🔄 Verileri Çek / Güncelle", use_container_width=True):
    if run_scraper_func is not None:
        with st.spinner("Transfermarkt verileri çekiliyor... Bu işlem kadrolar nedeniyle 5-10 dakika sürebilir."):
            try:
                run_scraper_func()
                st.sidebar.success("Veriler başarıyla güncellendi!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Veri çekilirken hata oluştu: {e}")
    else:
        st.sidebar.error("Hata: run_scraper.py bulunamadı veya hatalı!")

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
            st.dataframe(df_leagues, width="stretch")
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
                st.dataframe(pd.DataFrame(club_list), width="stretch")
            else:
                st.warning("Bu lig için henüz kulüp verisi çekilmemiş.")
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
                st.dataframe(pd.DataFrame(player_list), width="stretch")
            else:
                st.info("Bu kulübün oyuncu listesi henüz çekilmemiş.")
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
                st.dataframe(pd.DataFrame(match_list), width="stretch")
            else:
                st.info("Maç verisi bulunamadı.")
    finally:
        db.close()

elif page == "Statistics":
    st.title("📈 İstatistiksel Özet")
    db = get_db()
    try:
        # Lig bazlı kadro değerleri
        data = db.query(League.name, func.sum(Club.market_value)).join(Club).group_by(League.name).all()
        if data:
            df = pd.DataFrame(data, columns=["Lig", "Toplam Değer (M€)"])
            fig = px.pie(df, values="Toplam Değer (M€)", names="Lig", title="Liglerin Ekonomik Dağılımı")
            st.plotly_chart(fig, use_container_width=True)
            
            # En değerli 10 kulüp
            top_clubs = db.query(Club.name, Club.market_value).order_by(Club.market_value.desc()).limit(10).all()
            df_top = pd.DataFrame(top_clubs, columns=["Kulüp", "Değer (M€)"])
            fig2 = px.bar(df_top, x="Kulüp", y="Değer (M€)", color="Değer (M€)", title="Avrupa'nın En Değerli 10 Kulübü")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("İstatistik oluşturmak için yeterli veri yok.")
    finally:
        db.close()