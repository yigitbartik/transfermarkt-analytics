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
                # 1. Takımları çek
                clubs_data = clubs_scraper.scrape_clubs(league_info["url_slug"], code)
                
                # 2. Veritabanına kaydet
                for club_info in clubs_data:
                    # Daha önce eklenmiş mi kontrol et
                    existing_club = db.query(Club).filter(Club.name == club_info['name']).first()
                    
                    if not existing_club:
                        # PİYASA DEĞERİ TEMİZLEME: '€344.75m' -> 344.75
                        raw_value = club_info.get('market_value', '0')
                        # Sadece sayıları ve noktayı tutuyoruz
                        clean_value = re.sub(r'[^\d.]', '', raw_value.replace('bn', '000').replace('m', ''))
                        
                        try:
                            # Eğer modelin sayı bekliyorsa sayıya çeviriyoruz, hata alırsak 0 diyoruz
                            final_value = float(clean_value) if clean_value else 0.0
                        except:
                            final_value = 0.0

                        new_club = Club(
                            name=club_info['name'],
                            league_id=current_league.id,
                            # Modelin string bekliyorsa raw_value, sayı bekliyorsa final_value gönder
                            market_value=str(raw_value) 
                        )
                        db.add(new_club)
                
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