"""Matches scraper for Transfermarkt"""
import requests
from bs4 import BeautifulSoup
from config import TRANSFERMARKT_BASE_URL as BASE_URL, REQUEST_TIMEOUT, USER_AGENT
import logging
import time

logger = logging.getLogger(__name__)

class MatchesScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def scrape_matches(self, league_code, league_slug):
        try:
            url = f"{self.base_url}/fixtures/spieltag/wettbewerb/{league_code}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            matches = []
            current_date = None 
            
            rows = soup.find_all('tr')
            for row in rows:
                try:
                    row_classes = row.get('class', [])
                    if 'taggeszeile' in row_classes:
                        current_date = row.text.strip()
                        continue
                    
                    res_cell = row.find('td', class_='zeile-ergebnis')
                    if not res_cell or not res_cell.find('a'): continue
                    
                    link = res_cell.find('a')
                    m_id = link.get('href', '').split('/')[-1]
                    score = link.text.strip()
                    if not m_id: continue
                    
                    teams = row.find_all('td', class_='spieltagsansicht-vereinsname')
                    if len(teams) < 2: continue
                    
                    h_link = teams[0].find('a')
                    a_link = teams[1].find('a')
                    if not h_link or not a_link: continue
                    
                    h_id = h_link.get('href', '').split('verein/')[1].split('/')[0] if 'verein/' in h_link.get('href', '') else None
                    a_id = a_link.get('href', '').split('verein/')[1].split('/')[0] if 'verein/' in a_link.get('href', '') else None
                    if not h_id or not a_id: continue
                    
                    h_goals, a_goals = None, None
                    status = 'Scheduled'
                    if ':' in score and score != "-:-":
                        try:
                            parts = score.split(':')
                            h_goals = int(parts[0].strip())
                            a_goals = int(parts[1].strip())
                            status = 'Finished'
                        except: pass
                    
                    match_time = None
                    time_cell = row.find('td', class_='zeit')
                    if time_cell: match_time = time_cell.text.strip()
                    
                    matches.append({
                        'transfermarkt_id': m_id,
                        'home_club_id': h_id,
                        'away_club_id': a_id,
                        'home_goals': h_goals,
                        'away_goals': a_goals,
                        'status': status,
                        'match_date': current_date,
                        'match_time': match_time
                    })
                    time.sleep(0.05)
                except Exception:
                    continue
            return matches
        except Exception:
            return []