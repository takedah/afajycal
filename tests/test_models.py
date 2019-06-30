import unittest
from datetime import datetime, date, timedelta, timezone
from afajycal.models import MatchSchedule


class TestMatchSchedule(unittest.TestCase):
    def setUp(self):
        self.JST = timezone(timedelta(hours=+9), 'JST')
        self.schedule = MatchSchedule(**{
            'number': 480,
            'category': 'サテライト',
            'match_number': 'ST61',
            'match_date': date(2019, 6, 2),
            'kickoff_time': datetime(
                2019, 6, 2, 14, 0, tzinfo=self.JST),
            'home_team': '六合',
            'away_team': '中富良野',
            'studium': '花咲球技場'})


if __name__ == '__main__':
    unittest.main()
