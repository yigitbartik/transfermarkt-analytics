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
        """Bir kulübün kadrosundaki oyuncuları çeker"""
        try:
            # KRİTİK DÜZELTME: URL formatı /squad/kader/... olarak güncellendi
            url = f"{self.base_url}/squad/kader/verein/{club_id}/plus/1"
            logger.info(f"Scraping players from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            players = []
            
            # Oyuncu tablosunu bul
            player_rows = soup.select('table.items > tbody > tr')
            
            for row in player_rows:
                name_cell = row.find('td', class_='hauptlink')
                if not name_cell: continue
                    
                try:
                    name_tag = name_cell.find('a')
                    if not name_tag: continue
                    
                    p_name = name_tag.text.strip()
                    p_href = name_tag.get('href', '')
                    p_id = p_href.split('spieler/')[1].split('/')[0] if 'spieler/' in p_href else None

                    # Mevki
                    position = "N/A"
                    pos_table = row.find('table', class_='inline-table')
                    if pos_table:
                        pos_rows = pos_table.find_all('tr')
                        if len(pos_rows) > 1: 
                            position = pos_rows[1].text.strip()

                    # Yaş
                    zentriert = row.find_all('td', class_='zentriert')
                    age = None
                    if len(zentriert) > 2:
                        age_txt = zentriert[2].text.strip()
                        age = int(age_txt) if age_txt.isdigit() else None

                    # Piyasa Değeri
                    mv_cell = row.select_one('td.rechts.hauptlink')
                    market_value = mv_cell.text.strip() if mv_cell else "0"

                    players.append({
                        'transfermarkt_id': p_id,
                        'name': p_name,
                        'position': position,
                        'age': age,
                        'market_value': market_value
                    })
                except Exception as e:
                    continue
            
            logger.info(f"Successfully scraped {len(players)} players for club ID: {club_id}")
            return players
        except Exception as e:
            logger.error(f"PlayersScraper Error for {club_id}: {e}")
            return []