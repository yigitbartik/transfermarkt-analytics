BASE_URL = "https://www.transfermarkt.com"

LEAGUES = {
    "TR": {"name": "Süper Lig", "country": "Turkey", "url_slug": "super-lig"},
    "EN": {"name": "Premier League", "country": "England", "url_slug": "premier-league"},
    "ES": {"name": "La Liga", "country": "Spain", "url_slug": "la-liga"},
    "DE": {"name": "Bundesliga", "country": "Germany", "url_slug": "bundesliga"},
    "IT": {"name": "Serie A", "country": "Italy", "url_slug": "serie-a"},
    "FR": {"name": "Ligue 1", "country": "France", "url_slug": "ligue-1"},
    "PT": {"name": "Primeira Liga", "country": "Portugal", "url_slug": "primeira-liga"},
    "NL": {"name": "Eredivisie", "country": "Netherlands", "url_slug": "eredivisie"},
    "BE": {"name": "Belgian Pro League", "country": "Belgium", "url_slug": "belgian-pro-league"},
    "GR": {"name": "Super League", "country": "Greece", "url_slug": "super-league"}
}

DATABASE_URL = "sqlite:///./transfermarkt.db"
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
RETRY_ATTEMPTS = 3
SCRAPE_HOUR = 0
SCRAPE_MINUTE = 0
