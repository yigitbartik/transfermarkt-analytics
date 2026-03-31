"""Main scraper with support for multiple data sources"""
import logging
import re
import time
from config import TRANSFERMARKT_LEAGUES, ENABLE_SOFASCORE, ENABLE_FOTMOB
from database import init_db, SessionLocal, DataSource
from database.models import League, Club, Player, Match, MatchStatistic
from scraper.clubs import ClubsScraper
from scraper.players import PlayersScraper
from scraper.matches import MatchesScraper
from scraper.sofascore import SofaScoreScraper
from scraper.fotmob import FotMobScraper
from sqlalchemy import func
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_market_value(value):
    """Parse market value string to float"""
    if not value or value in ["None", "0", "-", ""]:
        return 0.0
    try:
        num = re.sub(r'[^\d.]', '', str(value))
        val = float(num) if num else 0.0
        if 'bn' in str(value).lower():
            val *= 1000.0
        return val
    except:
        return 0.0

def sync_data_source_status(db, source_name, status, error_msg=None):
    """Update data source sync status"""
    try:
        ds = db.query(DataSource).filter(DataSource.name == source_name).first()
        if not ds:
            ds = DataSource(name=source_name)
            db.add(ds)
        
        ds.status = status
        ds.last_sync = datetime.utcnow()
        ds.error_message = error_msg
        db.commit()
    except Exception as e:
        logger.error(f"Error updating data source status: {e}")

def scrape_transfermarkt_data():
    """Scrape data from Transfermarkt"""
    logger.info("Starting Transfermarkt scraping...")
    db = SessionLocal()
    
    try:
        clubs_scraper = ClubsScraper()
        players_scraper = PlayersScraper()
        matches_scraper = MatchesScraper()
        
        for code, league_info in TRANSFERMARKT_LEAGUES.items():
            logger.info(f"Processing league: {league_info['name']}")
            
            # Create or get league
            league = db.query(League).filter(League.code == code).first()
            if not league:
                league = League(
                    code=code,
                    name=league_info["name"],
                    country=league_info["country"],
                    url_slug=league_info["url_slug"]
                )
                db.add(league)
                db.commit()
                db.refresh(league)
            
            # 1. Scrape Clubs
            try:
                clubs_data = clubs_scraper.scrape_clubs(league_info["url_slug"], code)
                logger.info(f"Scraped {len(clubs_data)} clubs for {league_info['name']}")
                
                for club_data in clubs_data:
                    existing_club = db.query(Club).filter(
                        Club.transfermarkt_id == club_data['transfermarkt_id']
                    ).first()
                    
                    mv = parse_market_value(club_data['market_value'])
                    
                    if not existing_club:
                        new_club = Club(
                            transfermarkt_id=club_data['transfermarkt_id'],
                            name=club_data['name'],
                            league_id=league.id,
                            market_value=mv,
                            stadium=club_data.get('stadium')
                        )
                        db.add(new_club)
                        db.flush()
                        existing_club = new_club
                    else:
                        existing_club.market_value = mv
                    
                    # 2. Scrape Players
                    try:
                        players_data = players_scraper.scrape_players(club_data['transfermarkt_id'])
                        logger.info(f"Scraped {len(players_data)} players for {club_data['name']}")
                        
                        for player_data in players_data:
                            existing_player = db.query(Player).filter(
                                Player.transfermarkt_id == player_data['transfermarkt_id']
                            ).first()
                            
                            p_mv = parse_market_value(player_data['market_value'])
                            
                            if not existing_player:
                                new_player = Player(
                                    transfermarkt_id=player_data['transfermarkt_id'],
                                    name=player_data['name'],
                                    position=player_data['position'],
                                    age=player_data.get('age'),
                                    market_value=p_mv,
                                    club_id=existing_club.id,
                                    country=player_data.get('country'),
                                    jersey_number=player_data.get('jersey_number')
                                )
                                db.add(new_player)
                            else:
                                existing_player.market_value = p_mv
                        
                        db.commit()
                    except Exception as e:
                        logger.error(f"Error scraping players for {club_data['name']}: {e}")
                        db.rollback()
                    
                    time.sleep(0.2)
            
            except Exception as e:
                logger.error(f"Error scraping clubs: {e}")
                db.rollback()
            
            # 3. Scrape Matches
            try:
                matches_data = matches_scraper.scrape_matches(code, league_info["url_slug"])
                logger.info(f"Scraped {len(matches_data)} matches for {league_info['name']}")
                
                for match_data in matches_data:
                    # Check if match already exists
                    existing_match = db.query(Match).filter(
                        Match.transfermarkt_id == match_data['transfermarkt_id']
                    ).first()
                    
                    # Get clubs by ID
                    home_club = db.query(Club).filter(
                        Club.transfermarkt_id == match_data['home_club_id']
                    ).first()
                    away_club = db.query(Club).filter(
                        Club.transfermarkt_id == match_data['away_club_id']
                    ).first()
                    
                    if home_club and away_club:
                        if not existing_match:
                            new_match = Match(
                                transfermarkt_id=match_data['transfermarkt_id'],
                                league_id=league.id,
                                home_club_id=home_club.id,
                                away_club_id=away_club.id,
                                home_goals=match_data['home_goals'],
                                away_goals=match_data['away_goals'],
                                status=match_data['status'],
                                match_date=match_data.get('match_date'),
                                match_time=match_data.get('match_time'),
                                data_sources=match_data.get('data_sources', {})
                            )
                            db.add(new_match)
                        else:
                            existing_match.home_goals = match_data['home_goals']
                            existing_match.away_goals = match_data['away_goals']
                            existing_match.status = match_data['status']
                
                db.commit()
            except Exception as e:
                logger.error(f"Error scraping matches: {e}")
                db.rollback()
        
        sync_data_source_status(db, 'transfermarkt', 'active')
        logger.info("Transfermarkt scraping completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Critical error in Transfermarkt scraping: {e}")
        sync_data_source_status(db, 'transfermarkt', 'error', str(e))
        return False
    finally:
        db.close()

def scrape_external_match_stats():
    """Scrape match statistics from external sources"""
    logger.info("Starting external source scraping...")
    db = SessionLocal()
    
    try:
        sofascore_scraper = SofaScoreScraper()
        fotmob_scraper = FotMobScraper()
        
        # Get matches without detailed statistics
        matches = db.query(Match).filter(
            Match.status == 'Finished'
        ).limit(50).all()  # Limit to avoid rate limiting
        
        for match in matches:
            try:
                logger.info(f"Getting stats for {match.home_club.name} vs {match.away_club.name}")
                
                # Try SofaScore
                if ENABLE_SOFASCORE and not match.sofascore_id:
                    try:
                        sofascore_match = sofascore_scraper.search_match(
                            match.home_club.sofascore_id or 0,
                            match.away_club.sofascore_id or 0
                        )
                        
                        if sofascore_match:
                            match.sofascore_id = sofascore_match['sofascore_id']
                            
                            # Get stats
                            stats = sofascore_scraper.get_match_stats(sofascore_match['sofascore_id'])
                            if stats:
                                stat_entry = MatchStatistic(**stats, match_id=match.id)
                                db.add(stat_entry)
                        
                        time.sleep(0.5)
                    except Exception as e:
                        logger.debug(f"SofaScore error: {e}")
                
                # Try FotMob
                if ENABLE_FOTMOB and not match.fotmob_id:
                    try:
                        fotmob_match = fotmob_scraper.search_match(
                            match.home_club.name,
                            match.away_club.name,
                            match.match_date
                        )
                        
                        if fotmob_match:
                            match.fotmob_id = fotmob_match['fotmob_id']
                            
                            # Get stats
                            stats = fotmob_scraper.get_match_stats(fotmob_match['fotmob_id'])
                            if stats:
                                stat_entry = MatchStatistic(**stats, match_id=match.id)
                                db.add(stat_entry)
                        
                        time.sleep(0.5)
                    except Exception as e:
                        logger.debug(f"FotMob error: {e}")
                
                db.commit()
                
            except Exception as e:
                logger.error(f"Error getting stats for match: {e}")
                db.rollback()
        
        sync_data_source_status(db, 'sofascore', 'active')
        sync_data_source_status(db, 'fotmob', 'active')
        logger.info("External source scraping completed")
        return True
        
    except Exception as e:
        logger.error(f"Critical error in external scraping: {e}")
        return False
    finally:
        db.close()

def run_scraper():
    """Main scraper function"""
    logger.info("=" * 50)
    logger.info("STARTING SCRAPER")
    logger.info("=" * 50)
    
    init_db()
    
    # Scrape Transfermarkt first
    transfermarkt_success = scrape_transfermarkt_data()
    
    # Then scrape external sources
    external_success = scrape_external_match_stats()
    
    logger.info("=" * 50)
    if transfermarkt_success and external_success:
        logger.info("SCRAPER COMPLETED SUCCESSFULLY")
    else:
        logger.warning("SCRAPER COMPLETED WITH ERRORS")
    logger.info("=" * 50)

if __name__ == "__main__":
    run_scraper()
