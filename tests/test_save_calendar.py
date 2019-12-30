import unittest
from unittest import mock
import os
import shutil
import tempfile
from datetime import date, datetime, timedelta, timezone
from afajycal.db import DB
from afajycal.calendar import Calendar
from afajycal.save_calendar import SaveCalendar


class TestSaveSchedule(unittest.TestCase):
    def setUp(self):
        JST = timezone(timedelta(hours=+9), "JST")
        data_list = [
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
        obj = mock.MagicMock(match_data=data_list)
        self.calendar = Calendar(obj)
        self.db = DB("tests/afajycal_test.db")
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        self.db.close()

    def test_to_csv(self):
        test_file = os.path.join(self.test_dir, "schedules.csv")
        save_calendar = SaveCalendar({"calendar": self.calendar, "db": self.db})
        result = save_calendar.to_csv(test_file)
        with open(test_file, "r") as f:
            output = f.read()
        expect = (
            "480,サテライト,ST61,2019-06-02,2019-06-02 14:00:00+09:00,六合,中富良野,花咲球技場"
            + "\n"
            + "469,サテライト,ST50,2019-06-08,2019-06-08 14:00:00+09:00,永山南,六合,花咲球技場"
            + "\n"
        )
        self.assertEqual(output, expect)
        self.assertTrue(result)

    def test_to_db(self):
        save_calendar = SaveCalendar({"calendar": self.calendar, "db": self.db})
        result = save_calendar.to_db()
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
