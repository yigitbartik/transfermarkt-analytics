import logging
from config import LEAGUES
from database.db import init_db, SessionLocal
from database.models import League
from scraper.clubs import ClubsScraper
from scraper.players import PlayersScraper
from scraper.matches import MatchesScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_leagues():
    """Initialize leagues in database"""
    db = SessionLocal()
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
    finally:
        db.close()

def run_scraper():
    """Main scraper function"""
    logger.info("Starting scraper...")
    
    init_db()
    initialize_leagues()
    
    clubs_scraper = ClubsScraper()
    players_scraper = PlayersScraper()
    matches_scraper = MatchesScraper()
    
    for code, league_info in LEAGUES.items():
        logger.info(f"Processing league: {league_info['name']}")
        
        try:
            clubs = clubs_scraper.scrape_clubs(league_info["url_slug"], code)
            logger.info(f"Scraped {len(clubs)} clubs for {league_info['name']}")
            
            matches = matches_scraper.scrape_matches(code, league_info["url_slug"])
            logger.info(f"Scraped {len(matches)} matches for {league_info['name']}")
            
        except Exception as e:
            logger.error(f"Error processing {league_info['name']}: {e}")
            continue
    
    logger.info("Scraper finished successfully")

if __name__ == "__main__":
    run_scraper()
