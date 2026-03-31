"""Scraper package"""
from scraper.clubs import ClubsScraper
from scraper.players import PlayersScraper
from scraper.matches import MatchesScraper
from scraper.fotmob import FotMobScraper
from scraper.sofascore import SofaScoreScraper

__all__ = [
    'ClubsScraper',
    'PlayersScraper',
    'MatchesScraper',
    'FotMobScraper',
    'SofaScoreScraper',
]
