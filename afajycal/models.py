import urllib.parse
from datetime import datetime, timedelta, timezone


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
    kickoff_time : str
        match kickoff datetime
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

    def google_calendar_link(self):
        """
        output a url string for adding to google calendar.

        Returns
        -------
        link : str
            a url for adding to google calendar.

        """
        title = self.category + ' (' + self.home_team + ' vs ' \
            + self.away_team + ')'
        start_date = datetime.strptime(
                self.kickoff_time[:19] + '+0900', '%Y-%m-%d %H:%M:%S%z')
        start_date = start_date.astimezone(timezone.utc)
        if self.category == 'サテライト':
            game_time = 60
        else:
            game_time = 90

        end_date = start_date + timedelta(minutes=game_time)
        start_date_str = start_date.strftime('%Y%m%dT%H%M%SZ')
        end_date_str = end_date.strftime('%Y%m%dT%H%M%SZ')
        link = 'https://www.google.com/calendar/event?' \
            + 'action=' + 'TEMPLATE' \
            + '&text=' + urllib.parse.quote(title) \
            + '&location=' + urllib.parse.quote(self.studium) \
            + '&dates=' + start_date_str + '/' + end_date_str
        return link
