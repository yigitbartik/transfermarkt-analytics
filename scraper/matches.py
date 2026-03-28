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
        """Ligdeki maç sonuçlarını ve fikstürü Transfermarkt'tan çeker"""
        try:
            # URL Yapısı: /lig-adi/spieltag/wettbewerb/LIG-KODU
            if season:
                url = f"{self.base_url}/{league_slug}/spieltag/wettbewerb/{league_code}/saison_id/{season}"
            else:
                url = f"{self.base_url}/{league_slug}/spieltag/wettbewerb/{league_code}"
            
            logger.info(f"Scraping matches from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            matches = []
            
            # Transfermarkt'taki maç satırları 'begegnungZeile' sınıfına sahip tr etiketleridir
            match_rows = soup.select('tr.begegnungZeile')
            
            # Eğer yukarıdaki seçici sonuç vermezse tüm tr'leri tara
            if not match_rows:
                match_rows = soup.find_all('tr')

            for row in match_rows:
                try:
                    # 1. Takım İsimlerini ve Kulüp ID'lerini Bul
                    # Takımlar 'spieltagsansicht-vereinsname' sınıfındaki td içindedir
                    team_cells = row.select('td.spieltagsansicht-vereinsname')
                    if len(team_cells) < 2:
                        continue # Maç satırı değilse atla
                    
                    home_link = team_cells[0].find('a')
                    away_link = team_cells[1].find('a')
                    
                    if not home_link or not away_link:
                        continue

                    # Kulüp ID'lerini linkten ayıkla (/verein/141 gibi)
                    home_tm_id = home_link['href'].split('verein/')[1].split('/')[0]
                    away_tm_id = away_link['href'].split('verein/')[1].split('/')[0]

                    # 2. Skor Hücresini ve Maç ID'sini Çek
                    # Skor 'zeile-ergebnis' sınıfındaki linkin içindedir
                    result_cell = row.find('td', class_='zeile-ergebnis')
                    if not result_cell:
                        continue
                        
                    result_link = result_cell.find('a')
                    if not result_link:
                        continue
                        
                    score_text = result_link.text.strip() # Örn: "2:1"
                    
                    # Maç ID'sini linkten çek (linkin sonundaki sayısal ID)
                    # Href genelde: /spielbericht/index/spielbericht/4345226
                    match_tm_id = result_link['href'].split('/')[-1]

                    # 3. Skoru Parçala
                    home_goals, away_goals = None, None
                    if ':' in score_text and score_text != "-:-":
                        parts = score_text.split(':')
                        # Sadece sayı olan skorları alıyoruz (erteleme vb. durumları elemek için)
                        if parts[0].strip().isdigit() and parts[1].strip().isdigit():
                            home_goals = int(parts[0].strip())
                            away_goals = int(parts[1].strip())

                    match_data = {
                        'transfermarkt_id': match_tm_id, # Veritabanındaki NOT NULL kısıtlaması için şart
                        'home_club_id': home_tm_id,
                        'away_club_id': away_tm_id,
                        'home_goals': home_goals,
                        'away_goals': away_goals,
                        'status': 'Finished' if home_goals is not None else 'Scheduled',
                        'match_date': None,
                        'match_time': None
                    }
                    matches.append(match_data)
                    
                except Exception as e:
                    # Bir satır hatalıysa durma, bir sonrakine geç
                    continue
            
            logger.info(f"Successfully scraped {len(matches)} matches for {league_slug}")
            return matches
            
        except Exception as e:
            logger.error(f"Error scraping matches: {e}")
            return []