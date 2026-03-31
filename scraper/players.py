"""Players scraper for Transfermarkt"""
import requests
from bs4 import BeautifulSoup
from config import TRANSFERMARKT_BASE_URL, REQUEST_TIMEOUT, USER_AGENT
import logging
import time

logger = logging.getLogger(__name__)

class PlayersScraper:
    def __init__(self):
        self.base_url = TRANSFERMARKT_BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def scrape_players(self, club_id):
        """Scrape players from a club squad"""
        try:
            url = f"{self.base_url}/squad/kader/verein/{club_id}/plus/1"
            logger.info(f"Scraping players from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            players = []
            
            # Find player table
            player_rows = soup.select('table.items > tbody > tr')
            
            if not player_rows:
                logger.warning(f"No player rows found for club {club_id}")
                return []
            
            for row in player_rows:
                try:
                    # Skip if it's a title row
                    if row.find('th'):
                        continue
                    
                    name_cell = row.find('td', class_='hauptlink')
                    if not name_cell:
                        continue
                    
                    name_tag = name_cell.find('a')
                    if not name_tag:
                        continue
                    
                    p_name = name_tag.text.strip()
                    p_href = name_tag.get('href', '')
                    p_id = p_href.split('spieler/')[1].split('/')[0] if 'spieler/' in p_href else None
                    
                    if not p_id:
                        continue
                    
                    # Position
                    position = "N/A"
                    pos_table = row.find('table', class_='inline-table')
                    if pos_table:
                        pos_rows = pos_table.find_all('tr')
                        if len(pos_rows) > 1:
                            position = pos_rows[1].text.strip()
                    
                    # Age
                    age = None
                    zentriert = row.find_all('td', class_='zentriert')
                    if len(zentriert) > 2:
                        age_txt = zentriert[2].text.strip()
                        try:
                            age = int(age_txt) if age_txt.isdigit() else None
                        except:
                            age = None
                    
                    # Jersey number
                    jersey = None
                    if len(zentriert) > 0:
                        jersey_txt = zentriert[0].text.strip()
                        try:
                            jersey = int(jersey_txt) if jersey_txt.isdigit() else None
                        except:
                            jersey = None
                    
                    # Market value
                    mv_cell = row.select_one('td.rechts.hauptlink')
                    market_value = mv_cell.text.strip() if mv_cell else "0"
                    
                    # Country (if available)
                    country = None
                    img_tags = row.find_all('img')
                    if img_tags:
                        for img in img_tags:
                            title = img.get('title', '')
                            if title and len(title) < 30:
                                country = title
                                break
                    
                    players.append({
                        'transfermarkt_id': p_id,
                        'name': p_name,
                        'position': position,
                        'age': age,
                        'jersey_number': jersey,
                        'market_value': market_value,
                        'country': country
                    })
                    time.sleep(0.05)
                    
                except Exception as e:
                    logger.debug(f"Error parsing player row: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(players)} players for club {club_id}")
            return players
            
        except Exception as e:
            logger.error(f"Error scraping players for club {club_id}: {e}")
            return []
