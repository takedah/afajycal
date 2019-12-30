import unittest
from unittest.mock import Mock, patch
from requests import Timeout, HTTPError
from datetime import date, datetime, timedelta, timezone
from afajycal.scraper import DownloadedHTML, HTMLDownloadError, ScrapedData


JST = timezone(timedelta(hours=+9), "JST")


def html_content():
    return """
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
    """


class TestDownloadedHTML(unittest.TestCase):
    def setUp(self):
        self.html_content = html_content()

    def tearDown(self):
        pass

    @patch("afajycal.scraper.requests")
    def test_content(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content
        )
        schedule_html = DownloadedHTML()
        result = schedule_html.content
        expect = self.html_content
        self.assertEqual(result, expect)

        mock_requests.get.side_effect = Timeout("Dummy Error.")
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML()

        mock_requests.get.side_effect = HTTPError("Dummy Error.")
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML()

        mock_requests.get.side_effect = ConnectionError("Dummy Error.")
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML()

        mock_requests.get.return_value = Mock(status_code=404)
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML()


class TestScrapedData(unittest.TestCase):
    def setUp(self):
        self.html_content = html_content()

    def tearDown(self):
        pass

    @patch("afajycal.scraper.requests")
    def test_data_list(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content
        )
        downloaded_html = DownloadedHTML()
        scraper = ScrapedData(downloaded_html)
        expect = [
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
        self.assertEqual(scraper.match_data, expect)

        # 想定外のテーブル要素があった場合は空リストを返す。
        dummy_table = """
        <table border="2">
          <tbody>
            <tr>
              <td>this</td><td>is</td><td>dummy</td>
            </tr>
          </tbody>
        </table>
        """
        mock_requests.get.return_value = Mock(status_code=200, content=dummy_table)
        downloaded_html = DownloadedHTML()
        scraper = ScrapedData(downloaded_html)
        self.assertEqual(scraper.match_data, [])
