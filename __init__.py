"""Transfermarkt Analytics Pro - Professional Football Analytics Platform"""

__version__ = "2.0.0"
__author__ = "Analytics Team"
__description__ = "Advanced football analytics with multi-source data integration"

# Import key modules
from database import init_db, get_db, SessionLocal
from run_scraper import run_scraper

__all__ = [
    'init_db',
    'get_db', 
    'SessionLocal',
    'run_scraper',
]
