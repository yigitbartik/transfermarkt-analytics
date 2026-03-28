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
    """'€344.75m' veya '€1.31bn' gibi metinleri sayıya çevirir"""
    if not value_str or value_str == "None" or value_str == "0":
        return 0.0
    try:
        # Sadece rakam ve noktaları al (Euro sembolü vb. temizle)
        number_part = re.sub(r'[^\d.]', '', value_str)
        value = float(number_part)
        
        # Milyon (m) veya Milyar (bn) kontrolü
        if 'bn' in value_str.lower():
            value *= 1000.0  # Milyar ise 1000 ile çarp (Milyon cinsinden tutmak için)
        
        return value
    except:
        return 0.0

def initialize_leagues(db):
    """Initialize leagues in database"""
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
    """Main scraper function"""
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
                # 1. KULÜPLERİ ÇEK
                clubs_data = clubs_scraper.scrape_clubs(league_info["url_slug"], code)
                
                # 2. VERİTABANINA KAYDET
                for club_info in clubs_data:
                    if not club_info['name']:
                        continue
                        
                    existing_club = db.query(Club).filter(Club.name == club_info['name']).first()
                    
                    # Piyasada metni (örn: €344.75m) sayıya çeviriyoruz
                    final_market_value = parse_market_value(club_info.get('market_value', '0'))

                    if not existing_club:
                        new_club = Club(
                            name=club_info['name'],
                            league_id=current_league.id,
                            market_value=final_market_value # ARTIK SAYI OLARAK GİDİYOR
                        )
                        db.add(new_club)
                    else:
                        # Varsa değerini güncelle
                        existing_club.market_value = final_market_value
                
                db.commit()
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