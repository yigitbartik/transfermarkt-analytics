import logging
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
    db = SessionLocal() # Veritabanı bağlantısını açtık
    
    try:
        initialize_leagues(db)
        
        clubs_scraper = ClubsScraper()
        players_scraper = PlayersScraper()
        matches_scraper = MatchesScraper()
        
        for code, league_info in LEAGUES.items():
            logger.info(f"Processing league: {league_info['name']}")
            
            # Hangi ligde olduğumuzu veritabanından buluyoruz
            current_league = db.query(League).filter(League.code == code).first()
            if not current_league:
                continue
            
            try:
                # 1. KULÜPLERİ ÇEK
                clubs = clubs_scraper.scrape_clubs(league_info["url_slug"], code)
                logger.info(f"Scraped {len(clubs)} clubs for {league_info['name']}")
                
                # 2. KULÜPLERİ VERİTABANINA KAYDET (EKRANLARA VERİ BURADAN GİDECEK!)
                for club_data in clubs:
                    # İsim boş değilse ve veritabanında daha önce yoksa ekle
                    if club_data['name']:
                        existing_club = db.query(Club).filter(Club.name == club_data['name']).first()
                        if not existing_club:
                            new_club = Club(
                                name=club_data['name'],
                                league_id=current_league.id,
                                market_value=club_data.get('market_value', '0'),
                                country=club_data.get('country'),
                                stadium=club_data.get('stadium')
                            )
                            db.add(new_club)
                
                # Değişiklikleri kaydet
                db.commit()
                logger.info(f"Saved clubs to database for {league_info['name']}")
                
                # 3. MAÇLARI ÇEK
                matches = matches_scraper.scrape_matches(code, league_info["url_slug"])
                logger.info(f"Scraped {len(matches)} matches for {league_info['name']}")
                
            except Exception as e:
                logger.error(f"Error processing {league_info['name']}: {e}")
                db.rollback()
                continue
        
        logger.info("Scraper finished successfully")
    finally:
        db.close()

if __name__ == "__main__":
    run_scraper()