import unittest
from unittest import mock
from datetime import date, datetime, timedelta, timezone
from afajycal.db import DB
from afajycal.schedule_finder import ScheduleFinder
from afajycal.calendar import Calendar
from afajycal.save_calendar import SaveCalendar


JST = timezone(timedelta(hours=+9), "JST")


class TestScheduleFinder(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        db_path = "tests/afajycal_test.db"
        match_data = [
            {
                "number": 480,
                "category": "サテライト",
                "match_number": "ST61",
                "match_date": date(2019, 6, 2),
                "kickoff_time": datetime(2019, 6, 2, 14, 0, tzinfo=JST),
                "home_team": "六合",
                "away_team": "中富良野",
                "studium": "花咲球技場",
            },
            {
                "number": 469,
                "category": "サテライト",
                "match_number": "ST50",
                "match_date": date(2019, 6, 8),
                "kickoff_time": datetime(2019, 6, 8, 14, 0, tzinfo=JST),
                "home_team": "永山南",
                "away_team": "六合",
                "studium": "花咲球技場",
            },
        ]
        obj = mock.MagicMock(match_data=match_data)
        self.calendar = Calendar(obj)
        self.db = DB(db_path)
        SaveCalendar({"calendar": self.calendar, "db": self.db}).to_db()
        self.schedule_finder = ScheduleFinder(self.db)

    @classmethod
    def tearDownClass(self):
        self.db.close()

    def test__trim_team_name(self):
        expect = "六合"
        self.assertEqual(self.schedule_finder._trim_team_name("旭川市立六合中学校"), expect)

    def test_find(self):
        self.schedule_finder.find({"team_name": "六合", "category": "サテライト"})
        result = self.schedule_finder.match_data[0]
        self.assertEqual(result["category"], "サテライト")
        self.assertEqual(result["away_team"], "中富良野")
        self.assertEqual(result["studium"], "花咲球技場")
        self.assertEqual(result["match_date"], date(2019, 6, 2))
        self.assertEqual(
            result["kickoff_time"], datetime(2019, 6, 2, 14, 0, tzinfo=JST)
        )
        self.schedule_finder.find({"match_date": date(2019, 9, 18)})
        self.assertEqual(self.schedule_finder.match_data, [])


if __name__ == "__main__":
    unittest.main()
