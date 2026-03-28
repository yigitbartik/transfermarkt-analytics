import logging
import re
from config import LEAGUES
from database.db import init_db, SessionLocal
from database.models import League, Club, Player, Match
from scraper.clubs import ClubsScraper
from scraper.players import PlayersScraper
from scraper.matches import MatchesScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_market_value(value_str):
    """'€344.75m' veya '€1.31bn' gibi metinleri sayıya (float) çevirir"""
    if not value_str or value_str in ["None", "0", "-", ""]:
        return 0.0
    try:
        # Gereksiz karakterleri temizle (Euro sembolü vb.)
        number_part = re.sub(r'[^\d.]', '', value_str)
        if not number_part:
            return 0.0
            
        value = float(number_part)
        
        # Milyar (bn) ise 1000 ile çarpıp milyon birimine çek
        if 'bn' in value_str.lower():
            value *= 1000.0
        
        return value
    except Exception as e:
        logger.warning(f"Market value parsing error for '{value_str}': {e}")
        return 0.0

def initialize_leagues(db):
    """Sistemdeki ligleri veritabanına tanımlar"""
    try:
        for code, league_info in LEAGUES.items():
            existing = db.query(League).filter(League.code == code).first()
            if not existing:
                league = League(
                    code=code,
                    name=league_info["name"],
                    country=league_info["country"],
                    url_slug=league_info["url_slug"]
                )
                db.add(league)
        db.commit()
        logger.info("Leagues initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing leagues: {e}")
        db.rollback()

def run_scraper():
    """Ana veri çekme ve veritabanı kayıt motoru"""
    logger.info("Starting scraper...")
    
    init_db()
    db = SessionLocal()
    
    try:
        initialize_leagues(db)
        clubs_scraper = ClubsScraper()
        
        for code, league_info in LEAGUES.items():
            logger.info(f"Processing league: {league_info['name']}")
            
            current_league = db.query(League).filter(League.code == code).first()
            if not current_league:
                continue
            
            try:
                # 1. Takım verilerini webden çek
                clubs_data = clubs_scraper.scrape_clubs(league_info["url_slug"], code)
                
                # 2. Takımları veritabanına işle
                for club_info in clubs_data:
                    if not club_info.get('name') or not club_info.get('transfermarkt_id'):
                        continue
                    
                    # Hem ID hem isme göre kontrol et (Hata riskini sıfırlar)
                    existing_club = db.query(Club).filter(
                        (Club.transfermarkt_id == club_info['transfermarkt_id']) | 
                        (Club.name == club_info['name'])
                    ).first()
                    
                    market_val = parse_market_value(club_info.get('market_value', '0'))

                    if not existing_club:
                        # YENİ KAYIT: Artık transfermarkt_id NULL gitmiyor!
                        new_club = Club(
                            transfermarkt_id=club_info['transfermarkt_id'],
                            name=club_info['name'],
                            league_id=current_league.id,
                            market_value=market_val,
                            country=league_info['country']
                        )
                        db.add(new_club)
                    else:
                        # GÜNCELLEME: Takım varsa sadece değerini güncelle
                        existing_club.market_value = market_val
                        # Eğer ID boşsa (eskiden kalan hatalı kayıtlar için) doldur
                        if not existing_club.transfermarkt_id:
                            existing_club.transfermarkt_id = club_info['transfermarkt_id']
                
                db.commit() # Lig bazında verileri kaydet
                logger.info(f"Saved {len(clubs_data)} clubs for {league_info['name']}")
                
            except Exception as e:
                logger.error(f"Error processing {league_info['name']}: {e}")
                db.rollback()
                continue
        
        logger.info("Scraper finished successfully")
    finally:
        db.close()

if __name__ == "__main__":
    run_scraper()