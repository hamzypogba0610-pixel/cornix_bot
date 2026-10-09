import os
from sqlalchemy import (
    Column, String, Integer, DateTime, Date, Float, create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Match(Base):
    __tablename__ = "matches"
    match_id = Column(String, primary_key=True)
    league = Column(String, index=True)
    season = Column(String)
    date = Column(DateTime, index=True)
    home_team = Column(String)
    away_team = Column(String)
    home_corners = Column(Integer)
    away_corners = Column(Integer)


class TeamFeature(Base):
    __tablename__ = "team_features"
    id = Column(Integer, primary_key=True, autoincrement=True)
    team = Column(String, index=True)
    league = Column(String, index=True)
    as_of_date = Column(Date, index=True)
    matches_played = Column(Integer)
    corners_for_avg = Column(Float)
    corners_against_avg = Column(Float)


def engine():
    url = os.environ.get("DATABASE_URL", "sqlite:///./cfcx.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return create_engine(url, future=True)


def init_db():
    Base.metadata.create_all(engine())


def session():
    return sessionmaker(bind=engine(), future=True)()
