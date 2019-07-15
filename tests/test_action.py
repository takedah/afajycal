import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from afajycal.action import MatchScheduleAction


class TestMatchScheduleAction(unittest.TestCase):
    def setUp(self):
        self.year = 2019
        self.JST = timezone(timedelta(hours=+9), 'JST')
        self.html_content = [{
            'number': 480,
            'category': 'サテライト',
            'match_number': 'ST61',
            'kickoff_time': datetime(
                self.year, 6, 2, 14, 0, tzinfo=self.JST),
            'home_team': '六合',
            'away_team': '中富良野',
            'studium': '花咲球技場'}, {
                'number': 469,
                'category': 'サテライト',
                'match_number': 'ST50',
                'kickoff_time': datetime(
                    self.year, 6, 8, 14, 0, tzinfo=self.JST),
                'home_team': '永山南',
                'away_team': '六合',
                'studium': '花咲球技場'}, {
                    'number': 480,
                    'category': 'test',
                    'match_number': 'test',
                    'kickoff_time': datetime(
                        self.year, 1, 1, 0, 0, tzinfo=self.JST),
                    'home_team': 'test',
                    'away_team': 'test',
                    'studium': 'test'}]

    @patch('afajycal.action.Scraper.get_schedule_list')
    @patch('afajycal.action.Config')
    def test_create(self, config_mock, scraper_mock):
        config_mock.DATABASE = 'tests/afajycal_test.db'
        scraper_mock.return_value = self.html_content
        result = MatchScheduleAction.create()
        expect = True
        self.assertEqual(result, expect)

    @patch('afajycal.action.Config')
    def test_get_team_names(self, config_mock):
        config_mock.DATABASE = 'tests/afajycal_test.db'
        result = MatchScheduleAction.get_team_names()
        expect = ['六合', '永山南', '中富良野']
        self.assertEqual(result, expect)

    @patch('afajycal.action.Config')
    def test_get_number_of_matches(self, config_mock):
        config_mock.DATABASE = 'tests/afajycal_test.db'
        self.assertEqual(
                MatchScheduleAction.get_number_of_matches(
                    '六合', datetime(2019, 6, 2, 13, 0, tzinfo=self.JST)), 2)

    @patch('afajycal.action.Config')
    def test_get_categories(self, config_mock):
        config_mock.DATABASE = 'tests/afajycal_test.db'
        result = MatchScheduleAction.get_categories()
        expect = ['サテライト']
        self.assertEqual(result, expect)

    def test_trim_team_name(self):
        self.assertEqual(
            MatchScheduleAction._trim_team_name('旭川市立六合中学校'),
            '六合')

    @patch('afajycal.action.Config')
    def test_find(self, config_mock):
        config_mock.DATABASE = 'tests/afajycal_test.db'
        res = MatchScheduleAction.find(
                '六合', 'サテライト',
                datetime(2019, 6, 2, 13, 0, tzinfo=self.JST))
        schedule = res[0]
        number = res[1]
        self.assertEqual(schedule[0].away_team, '中富良野')
        self.assertEqual(schedule[0].studium, '花咲球技場')
        self.assertEqual(
            schedule[0].kickoff_time,
            datetime(2019, 6, 2, 14, 0, tzinfo=self.JST))
        self.assertEqual(schedule[1].home_team, '永山南')
        self.assertEqual(schedule[1].studium, '花咲球技場')
        self.assertEqual(
            schedule[1].kickoff_time,
            datetime(2019, 6, 8, 14, 0, tzinfo=self.JST))
        self.assertEqual(number, 2)
        res = MatchScheduleAction.find(
            '六合', 'サテライト',
            datetime(2019, 9, 18, 9, 0, tzinfo=self.JST))
        schedule = res[0]
        number = res[1]
        self.assertEqual(schedule, [])
        self.assertEqual(number, 0)


if __name__ == '__main__':
    unittest.main()
