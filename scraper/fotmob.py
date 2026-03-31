"""FotMob scraper for detailed match statistics"""
import requests
import logging
import json
from config import FOTMOB_API_URL, REQUEST_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)

class FotMobScraper:
    def __init__(self):
        self.api_url = FOTMOB_API_URL
        self.headers = {
            "User-Agent": USER_AGENT,
            "Referer": "https://www.fotmob.com/"
        }
        self.timeout = REQUEST_TIMEOUT
    
    def search_match(self, home_team, away_team, match_date):
        """Search for match on FotMob using team names and date"""
        try:
            # Search API endpoint for matches
            search_url = f"{self.api_url}/search"
            params = {
                'query': f"{home_team} vs {away_team}",
                'type': 'match'
            }
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'matches' in data and data['matches']:
                # Return first match found
                match = data['matches'][0]
                return {
                    'fotmob_id': match.get('id'),
                    'home_team': match.get('home', {}).get('name'),
                    'away_team': match.get('away', {}).get('name'),
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching match on FotMob: {e}")
            return None
    
    def get_match_stats(self, fotmob_match_id):
        """Get detailed match statistics from FotMob"""
        try:
            # Match details endpoint
            match_url = f"{self.api_url}/matchDetails"
            params = {'matchId': fotmob_match_id}
            
            response = requests.get(match_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'stats' not in data:
                return None
            
            stats = data['stats']
            
            # Extract key statistics
            match_stats = {
                'source': 'fotmob',
                'fotmob_id': fotmob_match_id,
                'home_possession': self._extract_stat(stats, 'possession', 'home'),
                'away_possession': self._extract_stat(stats, 'possession', 'away'),
                'home_shots_total': self._extract_stat(stats, 'shotsTotal', 'home'),
                'away_shots_total': self._extract_stat(stats, 'shotsTotal', 'away'),
                'home_shots_on_target': self._extract_stat(stats, 'shotsOnTarget', 'home'),
                'away_shots_on_target': self._extract_stat(stats, 'shotsOnTarget', 'away'),
                'home_passes_total': self._extract_stat(stats, 'passesTotal', 'home'),
                'away_passes_total': self._extract_stat(stats, 'passesTotal', 'away'),
                'home_pass_accuracy': self._extract_stat(stats, 'passAccuracy', 'home'),
                'away_pass_accuracy': self._extract_stat(stats, 'passAccuracy', 'away'),
                'home_fouls': self._extract_stat(stats, 'foulsCommitted', 'home'),
                'away_fouls': self._extract_stat(stats, 'foulsCommitted', 'away'),
                'home_corners': self._extract_stat(stats, 'corners', 'home'),
                'away_corners': self._extract_stat(stats, 'corners', 'away'),
                'home_tackles': self._extract_stat(stats, 'tackles', 'home'),
                'away_tackles': self._extract_stat(stats, 'tackles', 'away'),
                'home_yellow_cards': self._extract_stat(stats, 'yellowCards', 'home'),
                'away_yellow_cards': self._extract_stat(stats, 'yellowCards', 'away'),
                'home_red_cards': self._extract_stat(stats, 'redCards', 'home'),
                'away_red_cards': self._extract_stat(stats, 'redCards', 'away'),
            }
            
            return match_stats
            
        except Exception as e:
            logger.error(f"Error getting FotMob match stats: {e}")
            return None
    
    def _extract_stat(self, stats_dict, stat_name, team):
        """Helper to extract stat from FotMob response"""
        try:
            if stat_name in stats_dict:
                stat = stats_dict[stat_name]
                if isinstance(stat, dict):
                    if team == 'home':
                        return stat.get('home')
                    else:
                        return stat.get('away')
                return stat
            return None
        except:
            return None
    
    def get_league_matches(self, fotmob_league_id, season=None):
        """Get all matches for a league"""
        try:
            matches_url = f"{self.api_url}/leagues"
            params = {
                'id': fotmob_league_id,
                'tab': 'matches'
            }
            if season:
                params['season'] = season
            
            response = requests.get(matches_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            matches = []
            if 'matches' in data:
                for match in data['matches']:
                    matches.append({
                        'fotmob_id': match.get('id'),
                        'home_team': match.get('home', {}).get('name'),
                        'away_team': match.get('away', {}).get('name'),
                        'home_goals': match.get('homeGoals'),
                        'away_goals': match.get('awayGoals'),
                        'status': match.get('status'),
                        'date': match.get('date'),
                    })
            
            return matches
            
        except Exception as e:
            logger.error(f"Error getting FotMob league matches: {e}")
            return []
