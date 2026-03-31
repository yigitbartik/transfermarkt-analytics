"""SofaScore scraper for detailed match statistics and player data"""
import requests
import logging
from config import SOFASCORE_API_URL, REQUEST_TIMEOUT, USER_AGENT
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SofaScoreScraper:
    def __init__(self):
        self.api_url = SOFASCORE_API_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def search_team(self, team_name):
        """Search for team on SofaScore"""
        try:
            search_url = f"{self.api_url}/search/teams"
            params = {'queryString': team_name}
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'teams' in data and data['teams']:
                team = data['teams'][0]
                return {
                    'sofascore_id': team.get('id'),
                    'name': team.get('name'),
                    'country': team.get('country', {}).get('name'),
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching team on SofaScore: {e}")
            return None
    
    def search_match(self, home_team_id, away_team_id, date=None):
        """Search for a match between two teams"""
        try:
            search_url = f"{self.api_url}/search/matches"
            params = {
                'homeTeamId': home_team_id,
                'awayTeamId': away_team_id,
            }
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'matches' in data and data['matches']:
                # Return most recent match
                match = data['matches'][0]
                return {
                    'sofascore_id': match.get('id'),
                    'status': match.get('status'),
                    'date': match.get('startTimestamp'),
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching match on SofaScore: {e}")
            return None
    
    def get_match_stats(self, sofascore_match_id):
        """Get detailed match statistics from SofaScore"""
        try:
            match_url = f"{self.api_url}/match/{sofascore_match_id}/statistics"
            
            response = requests.get(match_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'statistics' not in data:
                return None
            
            stats = data['statistics']
            
            # Extract home and away team stats
            home_stats = {}
            away_stats = {}
            
            for stat_group in stats:
                for stat in stat_group.get('groups', []):
                    for item in stat.get('statisticsItems', []):
                        key = item.get('key')
                        home_val = item.get('homeTeam', {}).get('value')
                        away_val = item.get('awayTeam', {}).get('value')
                        
                        if home_val is not None:
                            home_stats[key] = home_val
                        if away_val is not None:
                            away_stats[key] = away_val
            
            # Map to our standard schema
            match_stats = {
                'source': 'sofascore',
                'sofascore_id': sofascore_match_id,
                'home_possession': home_stats.get('possessionPercentage'),
                'away_possession': away_stats.get('possessionPercentage'),
                'home_shots_total': home_stats.get('totalShots'),
                'away_shots_total': away_stats.get('totalShots'),
                'home_shots_on_target': home_stats.get('shotsOnTarget'),
                'away_shots_on_target': away_stats.get('shotsOnTarget'),
                'home_passes_total': home_stats.get('totalPasses'),
                'away_passes_total': away_stats.get('totalPasses'),
                'home_pass_accuracy': home_stats.get('passAccuracy'),
                'away_pass_accuracy': away_stats.get('passAccuracy'),
                'home_fouls': home_stats.get('fouls'),
                'away_fouls': away_stats.get('fouls'),
                'home_corners': home_stats.get('corners'),
                'away_corners': away_stats.get('corners'),
                'home_tackles': home_stats.get('tackles'),
                'away_tackles': away_stats.get('tackles'),
                'home_interceptions': home_stats.get('interceptions'),
                'away_interceptions': away_stats.get('interceptions'),
                'home_yellow_cards': home_stats.get('yellowCards'),
                'away_yellow_cards': away_stats.get('yellowCards'),
                'home_red_cards': home_stats.get('redCards'),
                'away_red_cards': away_stats.get('redCards'),
                'home_big_chances': home_stats.get('bigChances'),
                'away_big_chances': away_stats.get('bigChances'),
            }
            
            return match_stats
            
        except Exception as e:
            logger.error(f"Error getting SofaScore match stats: {e}")
            return None
    
    def get_match_events(self, sofascore_match_id):
        """Get match events (goals, cards, etc.)"""
        try:
            events_url = f"{self.api_url}/match/{sofascore_match_id}/events"
            
            response = requests.get(events_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            events = []
            if 'events' in data:
                for event in data['events']:
                    events.append({
                        'type': event.get('type'),
                        'minute': event.get('minute'),
                        'player': event.get('player', {}).get('name'),
                        'team': event.get('team', {}).get('name'),
                    })
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting SofaScore match events: {e}")
            return []
    
    def get_player_stats(self, sofascore_match_id, sofascore_player_id):
        """Get player performance statistics for a specific match"""
        try:
            player_url = f"{self.api_url}/match/{sofascore_match_id}/player/{sofascore_player_id}"
            
            response = requests.get(player_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            player_stats = {
                'source': 'sofascore',
                'sofascore_id': sofascore_player_id,
                'position': data.get('position'),
                'minutes_played': data.get('minutesPlayed'),
                'rating': data.get('rating'),
                'goals': data.get('goals'),
                'assists': data.get('assists'),
                'passes_completed': data.get('passesTotal'),
                'shots': data.get('shotsTotal'),
                'tackles': data.get('tackles'),
                'interceptions': data.get('interceptions'),
                'yellow_cards': data.get('yellowCards'),
                'red_cards': data.get('redCards'),
            }
            
            return player_stats
            
        except Exception as e:
            logger.error(f"Error getting SofaScore player stats: {e}")
            return None
    
    def get_league_matches(self, sofascore_league_id, season_id=None, days=7):
        """Get recent matches from a league"""
        try:
            # Get recent matches
            matches_url = f"{self.api_url}/sport/football/leagues/{sofascore_league_id}/events"
            
            params = {'limit': 50}
            if season_id:
                params['seasonId'] = season_id
            
            response = requests.get(matches_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            matches = []
            if 'events' in data:
                for match in data['events']:
                    matches.append({
                        'sofascore_id': match.get('id'),
                        'home_team': match.get('homeTeam', {}).get('name'),
                        'away_team': match.get('awayTeam', {}).get('name'),
                        'home_goals': match.get('homeScore', {}).get('current'),
                        'away_goals': match.get('awayScore', {}).get('current'),
                        'status': match.get('status'),
                        'start_timestamp': match.get('startTimestamp'),
                    })
            
            return matches
            
        except Exception as e:
            logger.error(f"Error getting SofaScore league matches: {e}")
            return []
