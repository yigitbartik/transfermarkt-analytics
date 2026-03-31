"""Database models for Transfermarkt Analytics"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class League(Base):
    __tablename__ = "leagues"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    country = Column(String(50), nullable=False)
    url_slug = Column(String(100), nullable=False)
    logo_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    clubs = relationship("Club", back_populates="league", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="league", cascade="all, delete-orphan")

class Club(Base):
    __tablename__ = "clubs"
    
    id = Column(Integer, primary_key=True)
    transfermarkt_id = Column(String(50), unique=True, nullable=False)
    sofascore_id = Column(String(50), unique=True, nullable=True)
    fotmob_id = Column(String(50), unique=True, nullable=True)
    whoscored_id = Column(String(50), unique=True, nullable=True)
    name = Column(String(150), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    country = Column(String(50))
    founded = Column(Integer)
    stadium = Column(String(150))
    logo_url = Column(String(500))
    website = Column(String(200))
    market_value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    league = relationship("League", back_populates="clubs")
    players = relationship("Player", back_populates="club", cascade="all, delete-orphan")
    home_matches = relationship("Match", back_populates="home_club", foreign_keys="Match.home_club_id")
    away_matches = relationship("Match", back_populates="away_club", foreign_keys="Match.away_club_id")

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True)
    transfermarkt_id = Column(String(50), unique=True, nullable=False)
    sofascore_id = Column(String(50), nullable=True)
    fotmob_id = Column(String(50), nullable=True)
    whoscored_id = Column(String(50), nullable=True)
    name = Column(String(150), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.id"))
    country = Column(String(50))
    position = Column(String(50))
    date_of_birth = Column(String(10))
    age = Column(Integer)
    jersey_number = Column(Integer)
    height = Column(String(10))
    weight = Column(String(10))
    market_value = Column(Float)
    photo_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    club = relationship("Club", back_populates="players")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True)
    transfermarkt_id = Column(String(50), nullable=True)
    sofascore_id = Column(String(50), nullable=True)
    fotmob_id = Column(String(50), nullable=True)
    whoscored_id = Column(String(50), nullable=True)
    
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    home_club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    away_club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    
    match_date = Column(String(10))
    match_time = Column(String(5))
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    status = Column(String(20))  # Scheduled, Finished, Live
    stadium = Column(String(150))
    attendance = Column(Integer)
    referee = Column(String(150))
    
    # Source tracking
    data_sources = Column(JSON)  # {'transfermarkt': True, 'sofascore': True, etc}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    league = relationship("League", back_populates="matches")
    home_club = relationship("Club", back_populates="home_matches", foreign_keys=[home_club_id])
    away_club = relationship("Club", back_populates="away_matches", foreign_keys=[away_club_id])
    statistics = relationship("MatchStatistic", back_populates="match", cascade="all, delete-orphan")

class MatchStatistic(Base):
    __tablename__ = "match_statistics"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    # Source of statistics
    source = Column(String(20))  # 'transfermarkt', 'whoscored', 'fotmob', 'sofascore'
    
    # Possession and control
    home_possession = Column(Float)
    away_possession = Column(Float)
    
    # Shots
    home_shots_total = Column(Integer)
    away_shots_total = Column(Integer)
    home_shots_on_target = Column(Integer)
    away_shots_on_target = Column(Integer)
    
    # Passes
    home_passes_total = Column(Integer)
    away_passes_total = Column(Integer)
    home_pass_accuracy = Column(Float)
    away_pass_accuracy = Column(Float)
    
    # Fouls and cards
    home_fouls = Column(Integer)
    away_fouls = Column(Integer)
    home_yellow_cards = Column(Integer)
    away_yellow_cards = Column(Integer)
    home_red_cards = Column(Integer)
    away_red_cards = Column(Integer)
    
    # Corners and throw-ins
    home_corners = Column(Integer)
    away_corners = Column(Integer)
    
    # Dribbles and tackles
    home_dribbles = Column(Integer)
    away_dribbles = Column(Integer)
    home_tackles = Column(Integer)
    away_tackles = Column(Integer)
    
    # Chances
    home_big_chances = Column(Integer)
    away_big_chances = Column(Integer)
    
    # Extra data as JSON for flexibility
    extra_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    match = relationship("Match", back_populates="statistics")

class PlayerPerformance(Base):
    __tablename__ = "player_performances"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    source = Column(String(20))  # 'whoscored', 'sofascore', 'fotmob'
    
    # Basic
    position_played = Column(String(50))
    minutes_played = Column(Integer)
    rating = Column(Float)  # 1-10 scale
    goals = Column(Integer)
    assists = Column(Integer)
    
    # Passing
    passes_completed = Column(Integer)
    passes_attempted = Column(Integer)
    pass_accuracy = Column(Float)
    
    # Possession
    touches = Column(Integer)
    possession_lost = Column(Integer)
    
    # Shooting
    shots = Column(Integer)
    shots_on_target = Column(Integer)
    
    # Defense
    tackles = Column(Integer)
    interceptions = Column(Integer)
    clearances = Column(Integer)
    fouls_committed = Column(Integer)
    fouls_drawn = Column(Integer)
    
    # Cards
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    
    # Dribbles and skills
    dribbles = Column(Integer)
    dribble_success = Column(Float)
    
    # Extra
    extra_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)  # 'transfermarkt', 'sofascore', 'fotmob', 'whoscored'
    last_sync = Column(DateTime)
    status = Column(String(20))  # 'active', 'inactive', 'error'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
