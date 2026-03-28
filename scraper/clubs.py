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
            # Doğru URL sıralaması
            url = f"{self.base_url}/{league_slug}/startseite/wettbewerb/{league_code}"
            logger.info(f"Scraping clubs from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            clubs = []
            
            # Transfermarkt'ın ana tablosunu bulacak şekilde HTML okuyucu güncellendi
            table = soup.find('table', class_='items')
            
            if table and table.find('tbody'):
                club_rows = table.find('tbody').find_all('tr', recursive=False)
            else:
                club_rows = soup.find_all('tr', class_=['odd', 'even'])
            
            for row in club_rows:
                try:
                    # 1. Takım Adını HTML'den Çekme
                    name_td = row.find('td', class_='hauptlink')
                    if not name_td:
                        continue
                    club_name = name_td.text.strip()
                    
                    # 2. Piyasa Değerini HTML'den Çekme
                    market_value_tds = row.find_all('td', class_='rechts')
                    market_value = market_value_tds[-1].text.strip() if market_value_tds else "0"
                    
                    # None yerine çektiğimiz gerçek verileri koyuyoruz!
                    club_data = {
                        'transfermarkt_id': None,
                        'name': club_name,
                        'country': None,
                        'stadium': None,
                        'logo_url': None,
                        'market_value': market_value
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