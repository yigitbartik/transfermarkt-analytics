"""Clubs scraper for Transfermarkt"""
import requests
from bs4 import BeautifulSoup
from config import TRANSFERMARKT_BASE_URL, REQUEST_TIMEOUT, USER_AGENT, RETRY_ATTEMPTS
import logging
import time

logger = logging.getLogger(__name__)

class ClubsScraper:
    def __init__(self):
        self.base_url = TRANSFERMARKT_BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def scrape_clubs(self, league_slug, league_code):
        """Scrape clubs from a league"""
        try:
            url = f"{self.base_url}/{league_slug}/startseite/wettbewerb/{league_code}"
            logger.info(f"Scraping clubs from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            clubs = []
            
            # Find main table
            table = soup.find('table', class_='items')
            if not table or not table.find('tbody'):
                logger.warning(f"No table found for {league_slug}")
                return []
            
            club_rows = table.find('tbody').find_all('tr', recursive=False)
            
            for row in club_rows:
                try:
                    # Find club name and link
                    name_td = row.find('td', class_='hauptlink')
                    if not name_td:
                        continue
                    
                    link_tag = name_td.find('a')
                    if not link_tag:
                        continue
                    
                    club_name = link_tag.text.strip()
                    club_href = link_tag.get('href', '')
                    
                    # Extract Transfermarkt ID
                    tm_id = None
                    if 'verein/' in club_href:
                        tm_id = club_href.split('verein/')[1].split('/')[0]
                    
                    if not tm_id:
                        continue
                    
                    # Extract market value
                    market_value_tds = row.find_all('td', class_='rechts')
                    market_value = market_value_tds[-1].text.strip() if market_value_tds else "0"
                    
                    # Try to find stadium (if available in row)
                    stadium = None
                    tds = row.find_all('td')
                    if len(tds) > 2:
                        stadium = tds[2].text.strip() if tds[2].text.strip() else None
                    
                    club_data = {
                        'transfermarkt_id': tm_id,
                        'name': club_name,
                        'market_value': market_value,
                        'stadium': stadium,
                        'country': None,
                        'logo_url': None
                    }
                    clubs.append(club_data)
                    time.sleep(0.05)  # Be nice to servers
                    
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
                'market_value': None,
                'founded': None,
                'website': None
            }
            
            # Try to extract name
            name_h1 = soup.find('h1')
            if name_h1:
                details['name'] = name_h1.text.strip()
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting club details for {club_id}: {e}")
            return None
