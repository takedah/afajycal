import unittest
from unittest import mock
from datetime import date, datetime, timedelta, timezone
from afajycal.db import DB
from afajycal.calendar import Calendar
from afajycal.save_calendar import SaveCalendar
from afajycal.schedule_service import ScheduleService


JST = timezone(timedelta(hours=+9), "JST")


class TestScheduleService(unittest.TestCase):
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
        self.schedule_service = ScheduleService(self.db)

    @classmethod
    def tearDownClass(self):
        self.db.close()

    def test_get_all_teams(self):
        expect = ["六合", "永山南", "中富良野"]
        self.assertEqual(self.schedule_service.get_all_teams(), expect)

    def test_get_all_categories(self):
        expect = ["サテライト"]
        self.assertEqual(self.schedule_service.get_all_categories(), expect)


if __name__ == "__main__":
    unittest.main()
