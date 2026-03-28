import logging
import re
import time
from config import LEAGUES
from database.db import init_db, SessionLocal
from database.models import League, Club, Player, Match
from scraper.clubs import ClubsScraper
from scraper.players import PlayersScraper
from scraper.matches import MatchesScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_mv(v):
    if not v or v in ["None", "0", "-", ""]: return 0.0
    try:
        num = re.sub(r'[^\d.]', '', str(v))
        val = float(num) if num else 0.0
        if 'bn' in str(v).lower(): val *= 1000.0
        return val
    except: return 0.0

def run_scraper():
    init_db()
    db = SessionLocal()
    c_scr, p_scr, m_scr = ClubsScraper(), PlayersScraper(), MatchesScraper()
    
    try:
        for code, info in LEAGUES.items():
            curr_league = db.query(League).filter(League.code == code).first()
            if not curr_league:
                curr_league = League(code=code, name=info["name"], country=info["country"], url_slug=info["url_slug"])
                db.add(curr_league)
                db.commit()
                db.refresh(curr_league)

            # 1. Clubs
            clubs_data = c_scr.scrape_clubs(info["url_slug"], code)
            for c in clubs_data:
                db_club = db.query(Club).filter(Club.transfermarkt_id == c['transfermarkt_id']).first()
                mv = parse_mv(c['market_value'])
                if not db_club:
                    db_club = Club(transfermarkt_id=c['transfermarkt_id'], name=c['name'], league_id=curr_league.id, market_value=mv)
                    db.add(db_club)
                    db.flush()
                else:
                    db_club.market_value = mv

                # 2. Players
                p_list = p_scr.scrape_players(c['transfermarkt_id'])
                for p in p_list:
                    db_p = db.query(Player).filter(Player.transfermarkt_id == p['transfermarkt_id']).first()
                    p_mv = parse_mv(p['market_value'])
                    if not db_p:
                        db.add(Player(transfermarkt_id=p['transfermarkt_id'], name=p['name'], position=p['position'], age=p['age'], market_value=p_mv, club_id=db_club.id))
                    else:
                        db_p.market_value = p_mv
                time.sleep(0.1)

            # 3. Matches
            m_list = m_scr.scrape_matches(code, info["url_slug"])
            for m in m_list:
                if not db.query(Match).filter(Match.transfermarkt_id == m['transfermarkt_id']).first():
                    h = db.query(Club).filter(Club.transfermarkt_id == m['home_club_id']).first()
                    a = db.query(Club).filter(Club.transfermarkt_id == m['away_club_id']).first()
                    if h and a:
                        db.add(Match(transfermarkt_id=m['transfermarkt_id'], home_club_id=h.id, away_club_id=a.id, home_goals=m['home_goals'], away_goals=m['away_goals'], league_id=curr_league.id, status=m['status']))
            db.commit()
    finally:
        db.close()