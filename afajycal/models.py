import urllib.parse
from datetime import timedelta


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
        start_date = self.kickoff_time
        if self.category == 'サテライト':
            game_time = 60
        else:
            game_time = 90

        end_date = self.kickoff_time + timedelta(minutes=game_time)
        start = start_date.strftime('%Y-%m-%dT%H:%M:%S%z')
        end = end_date.strftime('%Y-%m-%dT%H:%M:%S%z')
        link = 'https://www.google.com/calendar/event?' \
            + 'action=' + 'TEMPLATE' \
            + '&text=' + urllib.parse.quote(title) \
            + '&location=' + urllib.parse.quote(self.studium) \
            + '&dates=' + start + '/' + end
        return link
