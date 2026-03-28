from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class League(Base):
    __tablename__ = "leagues"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(2), unique=True, nullable=False)
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
    home_matches = relationship("Match", back_populates="home_club", foreign_keys="Match.home_club_id", cascade="all, delete-orphan")
    away_matches = relationship("Match", back_populates="away_club", foreign_keys="Match.away_club_id", cascade="all, delete-orphan")

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True)
    transfermarkt_id = Column(String(50), unique=True, nullable=False)
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
    transfermarkt_id = Column(String(50), unique=True, nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    home_club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    away_club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    match_date = Column(String(10))
    match_time = Column(String(5))
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    status = Column(String(20))
    stadium = Column(String(150))
    attendance = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    league = relationship("League", back_populates="matches")
    home_club = relationship("Club", back_populates="home_matches", foreign_keys=[home_club_id])
    away_club = relationship("Club", back_populates="away_matches", foreign_keys=[away_club_id])
