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
    """'€344.75m' veya '€1.31bn' gibi metinleri sayıya (float) çevirir"""
    if not value_str or value_str in ["None", "0", "-", "", "N/A"]:
        return 0.0
    try:
        # Sayı ve nokta dışındaki her şeyi temizle
        number_part = re.sub(r'[^\d.]', '', str(value_str))
        if not number_part:
            return 0.0
        val = float(number_part)
        # Milyar (bn) ise 1000 ile çarpıp milyon bazına getir
        if 'bn' in str(value_str).lower():
            val *= 1000.0
        return val
    except:
        return 0.0

def initialize_leagues(db):
    """Sistemdeki ligleri veritabanına tanımlar"""
    try:
        for code, info in LEAGUES.items():
            existing = db.query(League).filter(League.code == code).first()
            if not existing:
                league = League(
                    code=code,
                    name=info["name"],
                    country=info["country"],
                    url_slug=info["url_slug"]
                )
                db.add(league)
        db.commit()
    except Exception as e:
        logger.error(f"Lig başlatma hatası: {e}")
        db.rollback()

def run_scraper():
    """Ana veri çekme ve kayıt motoru"""
    logger.info("Scraper baslatiliyor...")
    init_db()
    db = SessionLocal()
    
    c_scr = ClubsScraper()
    p_scr = PlayersScraper()
    m_scr = MatchesScraper()
    
    try:
        initialize_leagues(db)
        
        for code, info in LEAGUES.items():
            logger.info(f"Lig isleniyor: {info['name']}")
            curr_league = db.query(League).filter(League.code == code).first()
            if not curr_league: continue
            
            try:
                # 1. KULÜPLERİ ÇEK
                clubs_data = c_scr.scrape_clubs(info["url_slug"], code)
                
                for c in clubs_data:
                    if not c.get('name') or not c.get('transfermarkt_id'): continue
                    
                    db_club = db.query(Club).filter(
                        (Club.transfermarkt_id == c['transfermarkt_id']) | (Club.name == c['name'])
                    ).first()
                    
                    m_val = parse_market_value(c.get('market_value', '0'))

                    if not db_club:
                        db_club = Club(
                            transfermarkt_id=c['transfermarkt_id'],
                            name=c['name'],
                            league_id=curr_league.id,
                            market_value=m_val,
                            country=info['country']
                        )
                        db.add(db_club)
                        db.flush() 
                    else:
                        db_club.market_value = m_val
                        if not db_club.transfermarkt_id: db_club.transfermarkt_id = c['transfermarkt_id']
                    
                    # 2. OYUNCULARI ÇEK
                    players = p_scr.scrape_players(c['transfermarkt_id'])
                    for p in players:
                        if not p.get('transfermarkt_id'): continue
                        db_p = db.query(Player).filter(Player.transfermarkt_id == p['transfermarkt_id']).first()
                        p_val = parse_market_value(p.get('market_value', '0'))
                        
                        if not db_p:
                            db.add(Player(
                                transfermarkt_id=p['transfermarkt_id'],
                                name=p['name'],
                                position=p.get('position'),
                                age=p.get('age'),
                                market_value=p_val,
                                club_id=db_club.id
                            ))
                        else:
                            db_p.market_value = p_val
                            db_p.club_id = db_club.id
                    
                    time.sleep(0.2) # TM engeline karsi

                # 3. MAÇLARI ÇEK
                matches = m_scr.scrape_matches(code, info["url_slug"])
                for m in matches:
                    if not m.get('transfermarkt_id'): continue
                    if not db.query(Match).filter(Match.transfermarkt_id == m['transfermarkt_id']).first():
                        h = db.query(Club).filter(Club.transfermarkt_id == m['home_club_id']).first()
                        a = db.query(Club).filter(Club.transfermarkt_id == m['away_club_id']).first()
                        if h and a:
                            db.add(Match(
                                transfermarkt_id=m['transfermarkt_id'],
                                home_club_id=h.id,
                                away_club_id=a.id,
                                home_goals=m['home_goals'],
                                away_goals=m['away_goals'],
                                status=m['status'],
                                league_id=curr_league.id
                            ))
                
                db.commit()
                logger.info(f"{info['name']} basariyla kaydedildi.")
                
            except Exception as e:
                logger.error(f"Lig hatasi {info['name']}: {e}")
                db.rollback()
                continue
                
        logger.info("Islem tamamlandi!")
    finally:
        db.close()

if __name__ == "__main__":
    run_scraper()