import requests
from bs4 import BeautifulSoup
from config import BASE_URL, REQUEST_TIMEOUT, USER_AGENT
import logging

class MatchesScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def scrape_matches(self, league_code, league_slug):
        try:
            url = f"{self.base_url}/{league_slug}/spieltag/wettbewerb/{league_code}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            matches = []
            
            rows = soup.find_all('tr')
            for row in rows:
                res_cell = row.find('td', class_='zeile-ergebnis')
                if not res_cell or not res_cell.find('a'): continue
                
                link = res_cell.find('a')
                m_id = link['href'].split('/')[-1]
                score = link.text.strip()
                
                teams = row.find_all('td', class_='spieltagsansicht-vereinsname')
                if len(teams) < 2: continue
                
                h_id = teams[0].find('a')['href'].split('verein/')[1].split('/')[0]
                a_id = teams[1].find('a')['href'].split('verein/')[1].split('/')[0]
                
                h_goals, a_goals = None, None
                if ':' in score and score != "-:-":
                    parts = score.split(':')
                    if parts[0].isdigit(): h_goals = int(parts[0])
                    if parts[1].isdigit(): a_goals = int(parts[1])

                matches.append({
                    'transfermarkt_id': m_id,
                    'home_club_id': h_id,
                    'away_club_id': a_id,
                    'home_goals': h_goals,
                    'away_goals': a_goals,
                    'status': 'Finished' if h_goals is not None else 'Scheduled'
                })
            return matches
        except:
            return []