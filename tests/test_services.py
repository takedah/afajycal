import unittest
from datetime import date, datetime

from afajycal.config import Config
from afajycal.db import DB
from afajycal.models import ScheduleFactory
from afajycal.services import ScheduleService

JST = Config.JST
test_data = [
    {
        "serial_number": 480,
        "category": "サテライト",
        "match_number": "ST61",
        "match_date": date(2019, 6, 2),
        "kickoff_time": datetime(2019, 6, 2, 14, 0, tzinfo=JST),
        "home_team": "六合",
        "away_team": "中富良野",
        "studium": "花咲球技場",
    },
    {
        "serial_number": 469,
        "category": "地区カブス",
        "match_number": "ST50",
        "match_date": date(2019, 6, 8),
        "kickoff_time": datetime(2019, 6, 8, 14, 0, tzinfo=JST),
        "home_team": "永山南",
        "away_team": "六合",
        "studium": "花咲球技場",
    },
]


class TestScheduleService(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.factory = ScheduleFactory()
        for row in test_data:
            self.factory.create(**row)
        self.db = DB()
        self.service = ScheduleService(self.db)

    @classmethod
    def tearDownClass(self):
        self.db.close()

    def test_create(self):
        self.service.truncate()
        for item in self.factory.items:
            self.assertTrue(self.service.create(item))
        self.db.commit()

    def test_find(self):
        found_schedules = self.service.find(team_name="旭川市立六合中学校", category="サテライト")
        result = found_schedules[0]
        self.assertEqual(result.category, "サテライト")
        self.assertEqual(result.away_team, "中富良野")
        self.assertEqual(result.studium, "花咲球技場")
        self.assertEqual(result.match_date, date(2019, 6, 2))
        self.assertEqual(result.kickoff_time, datetime(2019, 6, 2, 14, 0, tzinfo=JST))
        found_schedules = self.service.find(match_date=date(2019, 9, 18))
        self.assertEqual(found_schedules, [])

    def test_get_all_teams(self):
        expect = ["六合", "永山南", "中富良野"]
        self.assertEqual(self.service.get_all_teams(), expect)

    def test_get_all_categories(self):
        expect = ["サテライト", "地区カブス"]
        self.assertEqual(self.service.get_all_categories(), expect)


if __name__ == "__main__":
    unittest.main()
