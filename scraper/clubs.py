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
        """Scrape clubs from a league including their Transfermarkt IDs"""
        try:
            # Doğru URL yapısı: /lig-adi/startseite/wettbewerb/LIG-KODU
            url = f"{self.base_url}/{league_slug}/startseite/wettbewerb/{league_code}"
            logger.info(f"Scraping clubs from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            clubs = []
            
            # Ana takımlar tablosunu bul
            table = soup.find('table', class_='items')
            
            if table and table.find('tbody'):
                club_rows = table.find('tbody').find_all('tr', recursive=False)
            else:
                club_rows = soup.find_all('tr', class_=['odd', 'even'])
            
            for row in club_rows:
                try:
                    # Takım ismi ve linkini barındıran hücreyi bul
                    name_td = row.find('td', class_='hauptlink')
                    if not name_td:
                        continue
                    
                    link_tag = name_td.find('a')
                    if not link_tag:
                        continue
                        
                    club_name = link_tag.text.strip()
                    club_href = link_tag.get('href', '')
                    
                    # --- TRANSFERMARKT ID ÇIKARMA ---
                    # Href örneği: /galatasaray/startseite/verein/141/saison_id/2023
                    tm_id = None
                    if 'verein/' in club_href:
                        # 'verein/' kelimesinden sonraki ilk sayı grubunu alıyoruz
                        tm_id = club_href.split('verein/')[1].split('/')[0]
                    
                    if not tm_id:
                        continue # ID bulunamazsa veritabanı hata verir, bu yüzden atlıyoruz
                    
                    # Piyasa değerini çek (en sağdaki sütun)
                    market_value_tds = row.find_all('td', class_='rechts')
                    market_value = market_value_tds[-1].text.strip() if market_value_tds else "0"
                    
                    club_data = {
                        'transfermarkt_id': tm_id, # Artık NULL değil, gerçek ID!
                        'name': club_name,
                        'market_value': market_value,
                        'country': None,
                        'stadium': None,
                        'logo_url': None
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
            
            # Bu kısım detay sayfası için geliştirilebilir
            details = {
                'transfermarkt_id': club_id,
                'name': None,
                'market_value': None
            }
            return details
            
        except Exception as e:
            logger.error(f"Error getting club details: {e}")
            return None