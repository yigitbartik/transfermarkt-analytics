"""Matches scraper for Transfermarkt"""
import requests
from bs4 import BeautifulSoup
from config import TRANSFERMARKT_BASE_URL, REQUEST_TIMEOUT, USER_AGENT
import logging
import time
import re

logger = logging.getLogger(__name__)

class MatchesScraper:
    def __init__(self):
        self.base_url = TRANSFERMARKT_BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def scrape_matches(self, league_code, league_slug):
        """Scrape matches from a league"""
        try:
            url = f"{self.base_url}/fixtures/spieltag/wettbewerb/{league_code}"
            logger.info(f"Scraping matches from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            matches = []
            
            rows = soup.find_all('tr')
            
            # --- YENİ EKLENEN KISIM: Tarih Takibi ---
            current_date = None 
            
            for row in rows:
                try:
                    # --- YENİ EKLENEN KISIM: TARİH ÇEKİMİ ---
                    # Transfermarkt maçları güne göre gruplar. Başlık satırından tarihi alırız.
                    row_classes = row.get('class', [])
                    if 'taggeszeile' in row_classes:
                        current_date = row.text.strip()
                        continue
                    # ----------------------------------------
                    
                    res_cell = row.find('td', class_='zeile-ergebnis')
                    if not res_cell or not res_cell.find('a'):
                        continue
                    
                    link = res_cell.find('a')
                    m_id = link.get('href', '').split('/')[-1]
                    score = link.text.strip()
                    
                    if not m_id or m_id == '':
                        continue
                    
                    # Extract teams
                    teams = row.find_all('td', class_='spieltagsansicht-vereinsname')
                    if len(teams) < 2:
                        continue
                    
                    # Home team
                    h_link = teams[0].find('a')
                    if not h_link:
                        continue
                    h_id = h_link.get('href', '').split('verein/')[1].split('/')[0] if 'verein/' in h_link.get('href', '') else None
                    h_name = h_link.text.strip()
                    
                    # Away team
                    a_link = teams[1].find('a')
                    if not a_link:
                        continue
                    a_id = a_link.get('href', '').split('verein/')[1].split('/')[0] if 'verein/' in a_link.get('href', '') else None
                    a_name = a_link.text.strip()
                    
                    if not h_id or not a_id:
                        continue
                    
                    # Parse score
                    h_goals, a_goals = None, None
                    status = 'Scheduled'
                    
                    if ':' in score and score != "-:-":
                        try:
                            parts = score.split(':')
                            if parts[0].strip().isdigit():
                                h_goals = int(parts[0].strip())
                            if parts[1].strip().isdigit():
                                a_goals = int(parts[1].strip())
                            if h_goals is not None and a_goals is not None:
                                status = 'Finished'
                        except:
                            pass
                    
                    # --- YENİ EKLENEN KISIM: SAAT ÇEKİMİ ---
                    match_time = None
                    time_cell = row.find('td', class_='zeit')
                    if time_cell:
                        match_time = time_cell.text.strip()
                    # ----------------------------------------
                    
                    matches.append({
                        'transfermarkt_id': m_id,
                        'home_club_id': h_id,
                        'home_club_name': h_name,
                        'away_club_id': a_id,
                        'away_club_name': a_name,
                        'home_goals': h_goals,
                        'away_goals': a_goals,
                        'status': status,
                        'match_date': current_date, # YENİDEN DÜZENLENDİ
                        'match_time': match_time,   # YENİDEN DÜZENLENDİ
                        'data_sources': {'transfermarkt': True}
                    })
                    time.sleep(0.05)
                    
                except Exception as e:
                    logger.debug(f"Error parsing match row: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"Error scraping matches: {e}")
            return []
