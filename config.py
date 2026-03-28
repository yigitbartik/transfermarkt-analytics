BASE_URL = "https://www.transfermarkt.com"

# Transfermarkt'ın gerçek lig kodları ve doğru URL formatlarına göre güncellendi
LEAGUES = {
    "TR1": {"name": "Süper Lig", "country": "Turkey", "url_slug": "super-lig"},
    "GB1": {"name": "Premier League", "country": "England", "url_slug": "premier-league"},
    "ES1": {"name": "La Liga", "country": "Spain", "url_slug": "laliga"},
    "L1": {"name": "Bundesliga", "country": "Germany", "url_slug": "bundesliga"},
    "IT1": {"name": "Serie A", "country": "Italy", "url_slug": "serie-a"},
    "FR1": {"name": "Ligue 1", "country": "France", "url_slug": "ligue-1"},
    "PO1": {"name": "Primeira Liga", "country": "Portugal", "url_slug": "liga-portugal"},
    "NL1": {"name": "Eredivisie", "country": "Netherlands", "url_slug": "eredivisie"},
    "BE1": {"name": "Belgian Pro League", "country": "Belgium", "url_slug": "jupiler-pro-league"},
    "GR1": {"name": "Super League", "country": "Greece", "url_slug": "super-league-1"}
}

DATABASE_URL = "sqlite:///./transfermarkt.db"
REQUEST_TIMEOUT = 10
# Transfermarkt'ın bot sanmaması için daha güçlü bir User-Agent ekledik
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
RETRY_ATTEMPTS = 3
SCRAPE_HOUR = 0
SCRAPE_MINUTE = 0