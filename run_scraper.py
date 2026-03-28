import logging
import re
import time
from config import LEAGUES
from database.db import init_db, SessionLocal
from database.models import League, Club, Player, Match
from scraper.clubs import ClubsScraper
from scraper.players import PlayersScraper
from scraper.matches import MatchesScraper

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_market_value(value_str):
    """'€344.75m' veya '€1.31bn' metinlerini float sayıya çevirir"""
    if not value_str or value_str in ["None", "0", "-", ""]:
        return 0.0
    try:
        # Sayı ve nokta dışındaki her şeyi (euro sembolü, harfler) temizle
        number_part = re.sub(r'[^\d.]', '', str(value_str))
        if not number_part:
            return 0.0
            
        value = float(number_part)
        
        # Eğer milyar (bn) ise 1000 ile çarpıp milyon bazına getir
        if 'bn' in str(value_str).lower():
            value *= 1000.0
        
        return value
    except Exception as e:
        logger.warning(f"Market value parsing error for '{value_str}': {e}")
        return 0.0

def initialize_leagues(db):
    """Config dosyasındaki ligleri veritabanına ekler"""
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
    """Tüm veri çekme sürecini başlatan ana fonksiyon"""
    logger.info("Starting scraper engine...")
    
    init_db()
    db = SessionLocal()
    
    # Scraper sınıflarını başlat
    clubs_scraper = ClubsScraper()
    players_scraper = PlayersScraper()
    matches_scraper = MatchesScraper()
    
    try:
        initialize_leagues(db)
        
        for code, league_info in LEAGUES.items():
            logger.info(f"--- Processing league: {league_info['name']} ---")
            
            current_league = db.query(League).filter(League.code == code).first()
            if not current_league:
                continue
            
            try:
                # 1. KULÜPLERİ ÇEK
                clubs_data = clubs_scraper.scrape_clubs(league_info["url_slug"], code)
                
                for club_info in clubs_data:
                    if not club_info.get('name') or not club_info.get('transfermarkt_id'):
                        continue
                    
                    # Kulüp veritabanında var mı?
                    existing_club = db.query(Club).filter(
                        (Club.transfermarkt_id == club_info['transfermarkt_id']) | 
                        (Club.name == club_info['name'])
                    ).first()
                    
                    market_val = parse_market_value(club_info.get('market_value', '0'))

                    if not existing_club:
                        existing_club = Club(
                            transfermarkt_id=club_info['transfermarkt_id'],
                            name=club_info['name'],
                            league_id=current_league.id,
                            market_value=market_val,
                            country=league_info['country']
                        )
                        db.add(existing_club)
                        db.flush() # Oyuncular için ID oluşmasını sağlar
                    else:
                        existing_club.market_value = market_val
                    
                    # 2. OYUNCULARI ÇEK (Kulüp bazlı)
                    players_data = players_scraper.scrape_players(club_info['transfermarkt_id'])
                    for p_info in players_data:
                        if not p_info.get('transfermarkt_id'):
                            continue
                            
                        existing_player = db.query(Player).filter(
                            Player.transfermarkt_id == p_info['transfermarkt_id']
                        ).first()
                        
                        p_market_val = parse_market_value(p_info.get('market_value', '0'))
                        
                        if not existing_player:
                            new_player = Player(
                                transfermarkt_id=p_info['transfermarkt_id'],
                                name=p_info['name'],
                                position=p_info.get('position'),
                                age=p_info.get('age'),
                                market_value=p_market_val,
                                club_id=existing_club.id
                            )
                            db.add(new_player)
                        else:
                            existing_player.market_value = p_market_val
                            existing_player.club_id = existing_club.id
                    
                    # Transfermarkt bot korumasına yakalanmamak için kısa bekleme
                    time.sleep(0.3)

                # 3. MAÇLARI ÇEK
                matches_data = matches_scraper.scrape_matches(code, league_info["url_slug"])
                for m_info in matches_data:
                    if not m_info.get('transfermarkt_id'):
                        continue

                    existing_match = db.query(Match).filter(Match.transfermarkt_id == m_info['transfermarkt_id']).first()
                    
                    if not existing_match:
                        home_club = db.query(Club).filter(Club.transfermarkt_id == m_info['home_club_id']).first()
                        away_club = db.query(Club).filter(Club.transfermarkt_id == m_info['away_club_id']).first()
                        
                        if home_club and away_club:
                            new_match = Match(
                                transfermarkt_id=m_info['transfermarkt_id'],
                                home_club_id=home_club.id,
                                away_club_id=away_club.id,
                                home_goals=m_info['home_goals'],
                                away_goals=m_info['away_goals'],
                                status=m_info['status'],
                                league_id=current_league.id
                            )
                            db.add(new_match)
                
                db.commit() # Lig bittiğinde kaydet
                logger.info(f"Saved all data for league: {league_info['name']}")
                
            except Exception as e:
                logger.error(f"Error in league {league_info['name']}: {e}")
                db.rollback()
                continue
        
        logger.info("Full scraping process finished successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    run_scraper()