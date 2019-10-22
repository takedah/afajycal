import unittest
from afajycal.models import MatchSchedule


class TestMatchSchedule(unittest.TestCase):
    def setUp(self):
        self.schedule = MatchSchedule(
            **{
                "number": 480,
                "category": "サテライト",
                "match_number": "ST61",
                "match_date": "2019-06-02",
                "kickoff_time": "2019-06-02 14:00:00+09:00",
                "home_team": "六合",
                "away_team": "中富良野",
                "studium": "花咲球技場",
            }
        )

    def test_kickoff(self):
        expect = "2019/06/02 Sun 14:00"
        result = self.schedule.kickoff()
        self.assertEqual(result, expect)

    def test_google_calendar_link(self):
        expect = (
            "https://www.google.com/calendar/event?"
            + "action=TEMPLATE"
            + "&text="
            + "%E3%82%B5%E3%83%86%E3%83%A9%E3%82%A4%E3%83%88%20%28%E5%85%AD%"
            + "E5%90%88%20vs%20%E4%B8%AD%E5%AF%8C%E8%89%AF%E9%87%8E%29"
            + "&location="
            + "%E8%8A%B1%E5%92%B2%E7%90%83%E6%8A%80%E5%A0%B4"
            + "&dates="
            + "20190602T050000Z"
            + "/"
            + "20190602T060000Z"
        )
        result = self.schedule.google_calendar_link()
        self.assertEqual(result, expect)


if __name__ == "__main__":
    unittest.main()
