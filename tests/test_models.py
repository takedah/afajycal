import unittest
import urllib.parse
from datetime import date, datetime
from afajycal.db import DB
from afajycal.models import Schedule, ScheduleFactory, ScheduleService


test_data = [
    {
        "serial_number": 480,
        "category": "サテライト",
        "match_number": "ST61",
        "match_date": date(2019, 6, 2),
        "kickoff_time": datetime(2019, 6, 2, 14, 0),
        "home_team": "六合",
        "away_team": "中富良野",
        "studium": "花咲球技場",
    },
    {
        "serial_number": 469,
        "category": "サテライト",
        "match_number": "ST50",
        "match_date": date(2019, 6, 8),
        "kickoff_time": datetime(2019, 6, 8, 14, 0),
        "home_team": "永山南",
        "away_team": "六合",
        "studium": "花咲球技場",
    },
]


class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.schedule = Schedule(**test_data[0])

    def test_serial_number(self):
        self.assertEqual(self.schedule.serial_number, 480)

    def test_category(self):
        self.assertEqual(self.schedule.category, "サテライト")

    def test_match_number(self):
        self.assertEqual(self.schedule.match_number, "ST61")

    def test_match_date(self):
        self.assertEqual(self.schedule.match_date, date(2019, 6, 2))

    def test_kickoff_time(self):
        self.assertEqual(self.schedule.kickoff_time, datetime(2019, 6, 2, 14, 0))

    def test_home_team(self):
        self.assertEqual(self.schedule.home_team, "六合")

    def test_away_team(self):
        self.assertEqual(self.schedule.away_team, "中富良野")

    def test_studium(self):
        self.assertEqual(self.schedule.studium, "花咲球技場")

    def test_google_calendar_link(self):
        link_str = (
            "https://www.google.com/calendar/event?"
            + "action="
            + "TEMPLATE"
            + "&text="
            + urllib.parse.quote("サテライト (六合 vs 中富良野)")
            + "&location="
            + urllib.parse.quote("花咲球技場")
            + "&dates="
            + "20190602T050000Z"
            + "/"
            + "20190602T060000Z"
        )
        self.assertEqual(self.schedule.google_calendar_link, link_str)


class TestScheduleFactory(unittest.TestCase):
    def test_create(self):
        factory = ScheduleFactory()
        # Scheduleクラスのオブジェクトが生成できるか確認する。
        schedule = factory.create(test_data[0])
        self.assertTrue(isinstance(schedule, Schedule))


class TestScheduleService(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.factory = ScheduleFactory()
        for d in test_data:
            self.factory.create(d)
        self.db = DB("tests/afajycal_test.db")
        self.service = ScheduleService(self.db)

    @classmethod
    def tearDownClass(self):
        self.db.close()

    def test_create(self):
        self.service.truncate()
        for item in self.factory.items:
            result = self.service.create(item)
        self.db.commit()
        self.assertTrue(result)

    def test_find(self):
        found_schedules = self.service.find(team_name="旭川市立六合中学校", category="サテライト")
        result = found_schedules[0]
        self.assertEqual(result.category, "サテライト")
        self.assertEqual(result.away_team, "中富良野")
        self.assertEqual(result.studium, "花咲球技場")
        self.assertEqual(result.match_date, date(2019, 6, 2))
        self.assertEqual(result.kickoff_time, datetime(2019, 6, 2, 14, 0))
        found_schedules = self.service.find(match_date=date(2019, 9, 18))
        self.assertEqual(found_schedules, [])

    def test_get_all_teams(self):
        expect = ["六合", "永山南", "中富良野"]
        self.assertEqual(self.service.get_all_teams(), expect)

    def test_get_all_categories(self):
        expect = ["サテライト"]
        self.assertEqual(self.service.get_all_categories(), expect)


if __name__ == "__main__":
    unittest.main()
