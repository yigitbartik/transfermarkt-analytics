import requests
from bs4 import BeautifulSoup
from config import BASE_URL, REQUEST_TIMEOUT, USER_AGENT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClubsScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def scrape_clubs(self, league_slug, league_code):
        """Scrape clubs from a league"""
        try:
            # İŞTE DÜZELTİLEN SATIR: league_slug ve league_code yer değiştirdi!
            url = f"{self.base_url}/{league_slug}/startseite/wettbewerb/{league_code}"
            logger.info(f"Scraping clubs from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            clubs = []
            
            club_rows = soup.find_all('tr', class_='hover-action')
            
            for row in club_rows:
                try:
                    club_data = {
                        'transfermarkt_id': None,
                        'name': None,
                        'country': None,
                        'stadium': None,
                        'logo_url': None,
                        'market_value': None
                    }
                    clubs.append(club_data)
                except Exception as e:
                    logger.error(f"Error parsing club row: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(clubs)} clubs")
            return clubs
            
        except Exception as e:
            logger.error(f"Error scraping clubs: {e}")
            return []
    
    def get_club_details(self, club_id):
        """Get detailed information about a club"""
        try:
            url = f"{self.base_url}/verein/{club_id}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {
                'transfermarkt_id': club_id,
                'name': None,
                'country': None,
                'founded': None,
                'stadium': None,
                'website': None,
                'logo_url': None,
                'market_value': None
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting club details: {e}")
            return None