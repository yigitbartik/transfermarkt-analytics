import requests
from bs4 import BeautifulSoup
from config import BASE_URL, REQUEST_TIMEOUT, USER_AGENT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatchesScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def scrape_matches(self, league_code, league_slug, season=None):
        """Scrape matches from a league"""
        try:
            if season:
                url = f"{self.base_url}/{league_code}/spieltag/wettbewerb/{league_slug}/saison/{season}"
            else:
                url = f"{self.base_url}/{league_code}/spieltag/wettbewerb/{league_slug}"
            
            logger.info(f"Scraping matches from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            matches = []
            
            match_rows = soup.find_all('tr')
            
            for row in match_rows:
                try:
                    match_data = {
                        'transfermarkt_id': None,
                        'home_club_id': None,
                        'away_club_id': None,
                        'match_date': None,
                        'match_time': None,
                        'home_goals': None,
                        'away_goals': None,
                        'status': None,
                        'stadium': None,
                        'attendance': None
                    }
                    matches.append(match_data)
                except Exception as e:
                    logger.error(f"Error parsing match row: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"Error scraping matches: {e}")
            return []
