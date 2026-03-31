"""Players scraper for Transfermarkt - Enhanced Version"""
import requests
from bs4 import BeautifulSoup
from config import TRANSFERMARKT_BASE_URL as BASE_URL, REQUEST_TIMEOUT, USER_AGENT
import logging
import time

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlayersScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT

    def _parse_market_value(self, mv_text):
        """Piyasa değerini metinden sayıya çevirir (Örn: €15.00m -> 15.0)"""
        if not mv_text or mv_text == "-" or "0" in mv_text:
            return 0.0
        try:
            value = mv_text.replace('€', '').replace('m', '').replace('k', '').replace(',', '.').strip()
            num_value = float(value)
            if 'k' in mv_text: # Binlik değerse (thousand)
                num_value = num_value / 1000
            return num_value
        except Exception:
            return 0.0

    def scrape_players(self, club_id):
        """Bir kulübün tüm oyuncularını detaylı verilerle çeker"""
        try:
            # Kader (squad) sayfası en detaylı veriyi sunar
            url = f"{self.base_url}/kader/verein/{club_id}/plus/1"
            logger.info(f"Scraping players from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            players = []
            
            # Ana oyuncu tablosundaki satırları seçer
            player_rows = soup.select('table.items > tbody > tr')
            if not player_rows:
                logger.warning(f"No player rows found for club {club_id}")
                return []
            
            for row in player_rows:
                try:
                    # Başlık satırlarını atla
                    if row.find('th'): 
                        continue
                    
                    # 1. İSİM VE ID ÇEKİMİ
                    name_cell = row.find('td', class_='hauptlink')
                    if not name_cell: 
                        continue
                    
                    name_tag = name_cell.find('a')
                    if not name_tag: 
                        continue
                    
                    p_name = name_tag.text.strip()
                    p_href = name_tag.get('href', '')
                    
                    # ID'yi URL'den ayıkla
                    p_id = p_href.split('spieler/')[1].split('/')[0] if 'spieler/' in p_href else None
                    if not p_id: 
                        continue
                    
                    # 2. FOTOĞRAF ÇEKİMİ (Geliştirilmiş)
                    photo_url = None
                    # Transfermarkt bazen 'bilderrahmen-layout' bazen 'bilderrahmen-fixed' kullanır
                    photo_tag = row.find('img', class_=['bilderrahmen-layout', 'bilderrahmen-fixed'])
                    if photo_tag:
                        # Lazy load varsa data-src, yoksa src kullan
                        photo_url = photo_tag.get('data-src') or photo_tag.get('src')
                        if photo_url and 'small' in photo_url:
                            # Küçük resmi orta boyuta çevir (daha iyi görünür)
                            photo_url = photo_url.replace('small', 'medium')
                    
                    # 3. MEVKİ ÇEKİMİ
                    position = "N/A"
                    pos_table = row.find('table', class_='inline-table')
                    if pos_table:
                        pos_rows = pos_table.find_all('tr')
                        # İkinci satır mevkidir
                        if len(pos_rows) > 1: 
                            position = pos_rows[1].text.strip()
                    
                    # 4. YAŞ VE FORMA NUMARASI
                    zentriert = row.find_all('td', class_='zentriert')
                    
                    # Forma Numarası (0. hücre)
                    jersey = None
                    if len(zentriert) > 0:
                        jersey_txt = zentriert[0].text.strip()
                        jersey = int(jersey_txt) if jersey_txt.isdigit() else None
                    
                    # Yaş (2. hücre)
                    age = None
                    if len(zentriert) > 2:
                        age_txt = zentriert[2].text.strip()
                        # Parantez içindeki yaş formatını temizle (bazı sayfalarda (25) gibi gelebilir)
                        age_txt = "".join(filter(str.isdigit, age_txt))
                        age = int(age_txt) if age_txt else None
                    
                    # 5. PİYASA DEĞERİ (Sayısal değere çevrilmiş)
                    mv_cell = row.select_one('td.rechts.hauptlink')
                    raw_mv = mv_cell.text.strip() if mv_cell else "0"
                    market_value = self._parse_market_value(raw_mv)
                    
                    # 6. UYRUK (Ülke ismi)
                    country = None
                    flag_tag = row.select_one('img.flaggenrahmen')
                    if flag_tag:
                        country = flag_tag.get('title') or flag_tag.get('alt')
                    
                    players.append({
                        'transfermarkt_id': p_id,
                        'name': p_name,
                        'position': position,
                        'age': age,
                        'jersey_number': jersey,
                        'market_value': market_value,
                        'country': country,
                        'photo_url': photo_url
                    })
                    
                    # Sunucuya aşırı yüklenmemek için milisaniyelik bekleme
                    time.sleep(0.05)
                    
                except Exception as e:
                    logger.error(f"Error parsing player row: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(players)} players")
            return players
            
        except Exception as e:
            logger.error(f"Error scraping players from club {club_id}: {e}")
            return []