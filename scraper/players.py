import requests
from bs4 import BeautifulSoup
from config import BASE_URL, REQUEST_TIMEOUT, USER_AGENT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlayersScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def scrape_players(self, club_id):
        """Bir kulübün kadrosundaki oyuncuları güncel URL yapısıyla çeker"""
        try:
            # DOĞRU URL: Transfermarkt kadro sayfası için bu formatı kullanır
            url = f"{self.base_url}/id/kader/verein/{club_id}"
            logger.info(f"Scraping players from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            players = []
            
            # Oyuncuların listelendiği tabloyu bul
            # Transfermarkt'ta oyuncular 'items' sınıfına sahip tablonun içindedir
            player_rows = soup.select('table.items > tbody > tr')
            
            if not player_rows:
                # Yedek yöntem: Alternatif tablo sınıflarını dene
                player_rows = soup.find_all('tr', class_=['odd', 'even'])

            for row in player_rows:
                try:
                    # 1. İsim ve ID Çekme
                    # 'hauptlink' hücresindeki <a> etiketi
                    name_cell = row.find('td', class_='hauptlink')
                    if not name_cell:
                        continue
                        
                    name_tag = name_cell.find('a')
                    if not name_tag:
                        continue
                        
                    player_name = name_tag.text.strip()
                    player_href = name_tag.get('href', '')
                    
                    # Oyuncu ID'sini ayıkla (/spieler-adi/profil/spieler/12345)
                    p_id = None
                    if 'spieler/' in player_href:
                        p_id = player_href.split('spieler/')[1].split('/')[0]

                    # 2. Mevki Çekme
                    # Genelde ismin altındaki küçük tabloda yer alır
                    position = "N/A"
                    pos_detail = row.select_one('td.hauptlink + tr td') # Bazı tasarımlarda
                    if not pos_detail:
                        # Diğer tasarımda mevkii direkt yan sütundadır
                        all_tds = row.find_all('td')
                        if len(all_tds) > 4:
                            position = all_tds[4].text.strip()

                    # 3. Yaş ve Değer Çekme
                    # Transfermarkt'ta 'zentriert' sınıflı hücrelerden 3.sü genelde yaştır
                    zentriert_cells = row.find_all('td', class_='zentriert')
                    age = None
                    if len(zentriert_cells) > 2:
                        age_text = zentriert_cells[2].text.strip()
                        if age_text.isdigit():
                            age = int(age_text)

                    # Piyasa Değeri (Genelde 'rechts hauptlink' sınıfında)
                    mv_cell = row.find('td', class_='rechts hauptlink')
                    market_value = mv_cell.text.strip() if mv_cell else "0"

                    player_data = {
                        'transfermarkt_id': p_id,
                        'name': player_name,
                        'position': position,
                        'age': age,
                        'market_value': market_value,
                        'jersey_number': None # İstenirse eklenebilir
                    }
                    players.append(player_data)
                    
                except Exception as e:
                    continue
            
            logger.info(f"Successfully scraped {len(players)} players for club ID: {club_id}")
            return players
            
        except Exception as e:
            logger.error(f"Error scraping players for club {club_id}: {e}")
            return []