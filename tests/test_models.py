import unittest
import urllib.parse
from datetime import date, datetime

from afajycal.config import Config
from afajycal.models import Schedule, ScheduleFactory

JST = Config.JST
test_data = {
    "serial_number": 480,
    "category": "サテライト",
    "match_number": "ST61",
    "match_date": date(2019, 6, 2),
    "kickoff_time": datetime(2019, 6, 2, 14, 0, tzinfo=JST),
    "home_team": "六合",
    "away_team": "中富良野",
    "studium": "花咲球技場",
}


class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.schedule = Schedule(**test_data)

    def test_serial_number(self):
        self.assertEqual(self.schedule.serial_number, 480)

    def test_category(self):
        self.assertEqual(self.schedule.category, "サテライト")

    def test_match_number(self):
        self.assertEqual(self.schedule.match_number, "ST61")

    def test_match_date(self):
        self.assertEqual(self.schedule.match_date, date(2019, 6, 2))

    def test_kickoff_time(self):
        self.assertEqual(
            self.schedule.kickoff_time, datetime(2019, 6, 2, 14, 0, tzinfo=JST)
        )

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
        schedule = factory.create(**test_data)
        self.assertTrue(isinstance(schedule, Schedule))


if __name__ == "__main__":
    unittest.main()
