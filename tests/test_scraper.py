import unittest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import Mock, MagicMock, patch
from requests import Timeout, HTTPError
from afajycal.scraper import Scraper, HTMLDownloadError


class TestScraper(unittest.TestCase):
    def setUp(self):
        self.year = 2019
        self.JST = timezone(timedelta(hours=+9), 'JST')
        self.html_content = '''
          <table border="1">
          <tbody>
          <tr>
          <td>No.</td><td></td><td></td><td>M.No.</td>
          <td>節</td><td>月</td><td>日</td><td>G</td>
          <td>会場</td><td>KO</td><td>HOME</td><td></td>
          <td>AWAY</td>
          </tr>
          <tr>
          <td align="right">480</td>
          <td>サテライト</td>
          <td>サテライト</td>
          <td>ST61</td>
          <td align="right"></td>
          <td align="right">6</td>
          <td align="right">2</td>
          <td></td>
          <td>花咲球技場</td>
          <td>14:00</td>
          <td>六　合</td>
          <td>vs</td>
          <td>中富良野</td>
          </tr>
          <tr>
          <td align="right">469</td>
          <td>サテライト</td>
          <td>サテライト</td>
          <td>ST50</td>
          <td align="right"></td>
          <td align="right">6</td>
          <td align="right">8</td>
          <td></td>
          <td>花咲球技場</td>
          <td>14:00</td>
          <td>永山南</td>
          <td>vs</td>
          <td>六　合</td>
          </tr>
          <tr>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          </tr>
          </tbody>
          </table>
          '''
        self.method_mock = MagicMock(return_value=self.html_content)

    def tearDown(self):
        pass

    @patch('afajycal.scraper.requests')
    def test__download_html_content(self, mock_requests):
        scraper = Scraper()
        # Normal
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content)
        self.assertEqual(
            scraper._download_html_content(), self.html_content)
        # If HTTP request is timeout
        mock_requests.get.side_effect = Timeout('Dummy Error.')
        self.assertEqual(scraper._download_html_content(), None)
        # If HTTP request returns error code
        mock_requests.get.side_effect = HTTPError('Dummy Error.')
        self.assertEqual(scraper._download_html_content(), None)
        # If HTTP connection is error
        mock_requests.get.side_effect = ConnectionError('Dummy Error.')
        self.assertEqual(scraper._download_html_content(), None)
        # If HTTP request returns status code excepting 200
        mock_requests.get.return_value = Mock(status_code=404)
        self.assertEqual(scraper._download_html_content(), None)

    @patch('afajycal.scraper.requests')
    def test__html_to_list(self, mock_requests):
        scraper = Scraper()
        # Normal
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content)
        expect = [[
            '480', 'サテライト', 'サテライト',
            'ST61', '', '6',
            '2', '', '花咲球技場',
            '14:00', '六　合', 'vs',
            '中富良野'], [
                '469', 'サテライト', 'サテライト',
                'ST50', '', '6',
                '8', '', '花咲球技場',
                '14:00', '永山南', 'vs',
                '六　合'], [
                '', '', '',
                '', '', '',
                '', '', '',
                '', '', '',
                '']]
        self.assertEqual(scraper._html_to_list(), expect)
        # If this method can't get HTML content we assumed
        mock_requests.get.return_value = Mock(status_code=404)
        with self.assertRaises(HTMLDownloadError):
            scraper._html_to_list()

        # If HTML content this method getted doesn't have table
        # we assumed
        dummy_table = '''
        <table border="2">
          <tbody>
            <tr>
              <td>this</td><td>is</td><td>dummy</td>
            </tr>
          </tbody>
        </table>
        '''
        mock_requests.get.return_value = Mock(
            status_code=200, content=dummy_table)
        self.assertEqual(scraper._html_to_list(), [])

    def test__get_month(self):
        self.assertEqual(Scraper._get_month('4'), 4)
        self.assertEqual(Scraper._get_month('13'), 1)

    def test__get_day(self):
        self.assertEqual(Scraper._get_day('20'), 20)
        self.assertEqual(Scraper._get_day('0'), 1)

    def test__get_time(self):
        self.assertEqual(Scraper._get_time('14:10'), [14, 10])
        self.assertEqual(Scraper._get_time('1a:10'), [0, 0])

    def test__get_valid_year(self):
        self.assertEqual(Scraper._get_valid_year(4, 2019), 2019)
        self.assertEqual(Scraper._get_valid_year(2, 2019), 2020)

    def test_get_schedule_list(self):
        scraper = Scraper()
        scraper._download_html_content = self.method_mock
        expect = [{
            'number': 480,
            'category': 'サテライト',
            'match_number': 'ST61',
            'match_date': date(self.year, 6, 2),
            'kickoff_time': datetime(
                self.year, 6, 2, 14, 0, tzinfo=self.JST),
            'home_team': '六合',
            'away_team': '中富良野',
            'studium': '花咲球技場'}, {
                'number': 469,
                'category': 'サテライト',
                'match_number': 'ST50',
                'match_date': date(self.year, 6, 8),
                'kickoff_time': datetime(
                    self.year, 6, 8, 14, 0, tzinfo=self.JST),
                'home_team': '永山南',
                'away_team': '六合',
                'studium': '花咲球技場'}]
        self.assertEqual(scraper.get_schedule_list(), expect)


if __name__ == '__main__':
    unittest.main()
