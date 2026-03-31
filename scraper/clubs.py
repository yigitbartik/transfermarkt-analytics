"""Clubs scraper for Transfermarkt"""
import requests
from bs4 import BeautifulSoup
from config import TRANSFERMARKT_BASE_URL as BASE_URL, REQUEST_TIMEOUT, USER_AGENT
import logging
import time

logger = logging.getLogger(__name__)

class ClubsScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def scrape_clubs(self, league_slug, league_code):
        try:
            url = f"{self.base_url}/{league_slug}/startseite/wettbewerb/{league_code}"
            logger.info(f"Scraping clubs from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            clubs = []
            
            table = soup.find('table', class_='items')
            if not table or not table.find('tbody'):
                return []
            
            club_rows = table.find('tbody').find_all('tr', recursive=False)
            
            for row in club_rows:
                try:
                    name_td = row.find('td', class_='hauptlink')
                    if not name_td: continue
                    
                    link_tag = name_td.find('a')
                    if not link_tag: continue
                    
                    club_name = link_tag.text.strip()
                    club_href = link_tag.get('href', '')
                    
                    tm_id = None
                    if 'verein/' in club_href:
                        tm_id = club_href.split('verein/')[1].split('/')[0]
                    if not tm_id: continue
                    
                    # LOGO ÇEKİMİ
                    img_tag = row.select_one('td img')
                    logo_url = None
                    if img_tag:
                        logo_url = img_tag.get('data-src') or img_tag.get('src')
                        if logo_url:
                            logo_url = logo_url.replace('tiny', 'header').replace('small', 'header')
                    
                    market_value_tds = row.find_all('td', class_='rechts')
                    market_value = market_value_tds[-1].text.strip() if market_value_tds else "0"
                    
                    stadium = None
                    tds = row.find_all('td')
                    if len(tds) > 2:
                        stadium = tds[2].text.strip() if tds[2].text.strip() else None
                    
                    clubs.append({
                        'transfermarkt_id': tm_id,
                        'name': club_name,
                        'market_value': market_value,
                        'stadium': stadium,
                        'country': None,
                        'logo_url': logo_url
                    })
                    time.sleep(0.05)
                except Exception as e:
                    logger.error(f"Error parsing club row: {e}")
                    continue
            
            return clubs
        except Exception as e:
            logger.error(f"Error scraping clubs: {e}")
            return []