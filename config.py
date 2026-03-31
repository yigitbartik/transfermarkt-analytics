"""Configuration file for Transfermarkt Analytics"""

# ===== TRANSFERMARKT =====
TRANSFERMARKT_BASE_URL = "https://www.transfermarkt.com"
TRANSFERMARKT_LEAGUES = {
    "TR1": {"name": "Süper Lig", "country": "Turkey", "url_slug": "super-lig"},
    "GB1": {"name": "Premier League", "country": "England", "url_slug": "premier-league"},
    "ES1": {"name": "La Liga", "country": "Spain", "url_slug": "laliga"},
    "L1": {"name": "Bundesliga", "country": "Germany", "url_slug": "bundesliga"},
    "IT1": {"name": "Serie A", "country": "Italy", "url_slug": "serie-a"},
    "FR1": {"name": "Ligue 1", "country": "France", "url_slug": "ligue-1"},
}

# ===== FOTMOB API =====
FOTMOB_BASE_URL = "https://www.fotmob.com"
FOTMOB_API_URL = "https://api.fotmob.com"

# ===== WHOSCORED (AKA StatsBomb) =====
WHOSCORED_BASE_URL = "https://www.whoscored.com"

# ===== SOFASCORE =====
SOFASCORE_API_URL = "https://api.sofascore.com/api/v1"

# ===== DATABASE =====
DATABASE_URL = "sqlite:///./transfermarkt.db"

# ===== SCRAPING CONFIG =====
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
RETRY_ATTEMPTS = 3

# ===== CACHE SETTINGS =====
CACHE_ENABLED = True
CACHE_DURATION_HOURS = 24

# ===== LOGGING =====
LOG_LEVEL = "INFO"

# ===== FEATURE FLAGS =====
ENABLE_FOTMOB = True
ENABLE_WHOSCORED = True
ENABLE_SOFASCORE = True
ENABLE_MATCH_LINKING = True
ENABLE_STATS_AGGREGATION = True
