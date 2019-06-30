import sqlite3
from datetime import datetime, timedelta, timezone
from afajycal.config import Config
from afajycal.db import DB


class MatchSchedule:
    """
    AFA junior youth soccer match schedule.

    Attributes
    ----------
    number : int
        schedule item number
    category : str
        match category
    match_number : str
        serial number by division
    match_date : date
        match date
    kickoff_time : datetime
        match kickoff time
    home_team : str
        home team name
    away_team : str
        away team name
    studium : str
        match place
    """
    def __init__(self, **kwargs):
        self.number = kwargs['number']
        self.category = kwargs['category']
        self.match_number = kwargs['match_number']
        self.match_date = kwargs['match_date']
        self.kickoff_time = kwargs['kickoff_time']
        self.home_team = kwargs['home_team']
        self.away_team = kwargs['away_team']
        self.studium = kwargs['studium']
