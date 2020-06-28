import unittest
from datetime import date, datetime, timedelta, timezone
from requests import Timeout, HTTPError
from unittest.mock import Mock, patch
from afajycal.scraper import (
    DownloadedHTML,
    DownloadedExcel,
    HTMLDownloadError,
    ScrapedHTMLData,
    ScrapedExcelData,
)


JST = timezone(timedelta(hours=+9), "JST")


def html_content():
    return """
        <table border="1">
        <tbody>
        <tr>
        <td></td>
        <td>M.No.</td>
        <td>節</td>
        <td>月</td>
        <td>日</td>
        <td>C</td>
        <td>G</td>
        <td>会場</td>
        <td>KO</td>
        <td>HOME</td>
        <td></td>
        <td>AWAY</td>
        </tr>
        <tr>
        <td>480</td>
        <td>ST61</td>
        <td align="right"></td>
        <td align="right">6</td>
        <td align="right">2</td>
        <td>サテライト</td>
        <td></td>
        <td>花咲球技場</td>
        <td>14:00</td>
        <td>六　合</td>
        <td>vs</td>
        <td>中富良野</td>
        </tr>
        <tr>
        <td>469</td>
        <td>ST50</td>
        <td align="right"></td>
        <td align="right">6</td>
        <td align="right">8</td>
        <td>サテライト</td>
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
        </tr>
        </tbody>
        </table>
    """


def excel_content():
    return [
        [
            "M66",
            "AC38",
            "3",
            "8",
            "9",
            "D1",
            "B",
            "東光スポーツ公園A",
            "",
            "六　合",
            "vs",
            "留　萌",
            "82",
        ],
        [
            "M84",
            "AC56",
            "7",
            "10",
            "",
            "D1",
            "B",
            "東光スポーツ公園A",
            "15:30:00",
            "六　合",
            "vs",
            "TRAUM2nd",
            "104",
        ],
    ]


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
        schedule_html = DownloadedHTML("http://dummy.local")
        result = schedule_html.content
        expect = self.html_content
        self.assertEqual(result, expect)

        mock_requests.get.side_effect = Timeout("Dummy Error.")
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML("http://dummy.local")

        mock_requests.get.side_effect = HTTPError("Dummy Error.")
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML("http://dummy.local")

        mock_requests.get.side_effect = ConnectionError("Dummy Error.")
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML("http://dummy.local")

        mock_requests.get.return_value = Mock(status_code=404)
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML("http://dummy.local")


class TestDownloadedExcel(unittest.TestCase):
    def test_lists(self):
        schedule_excel = DownloadedExcel("tests/nittei2020_test.xlsx")
        result = schedule_excel.lists
        expect = excel_content()
        self.assertEqual(result[0], expect[0])
        self.assertEqual(result[1], expect[1])


class TestScrapedHTMLData(unittest.TestCase):
    def setUp(self):
        self.html_content = html_content()

    def tearDown(self):
        pass

    @patch("afajycal.scraper.requests")
    def test_data_list(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content
        )
        downloaded_html = DownloadedHTML("http://dummy.local")
        scraper = ScrapedHTMLData(downloaded_html)
        expect = [
            {
                "serial_number": "480",
                "category": "サテライト",
                "match_number": "ST61",
                "match_date": date(2020, 6, 2),
                "kickoff_time": datetime(2020, 6, 2, 14, 0),
                "home_team": "六合",
                "away_team": "中富良野",
                "studium": "花咲球技場",
            },
            {
                "serial_number": "469",
                "category": "サテライト",
                "match_number": "ST50",
                "match_date": date(2020, 6, 8),
                "kickoff_time": datetime(2020, 6, 8, 14, 0),
                "home_team": "永山南",
                "away_team": "六合",
                "studium": "花咲球技場",
            },
        ]
        self.assertEqual(scraper.schedule_data, expect)

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
        downloaded_html = DownloadedHTML("http://dummy.local")
        scraper = ScrapedHTMLData(downloaded_html)
        self.assertEqual(scraper.schedule_data, [])


class TestScrapedExcelData(unittest.TestCase):
    def setUp(self):
        self.downloaded_excel = DownloadedExcel("tests/nittei2020_test.xlsx")

    def tearDown(self):
        pass

    def test_data_list(self):
        scraper = ScrapedExcelData(self.downloaded_excel)
        expect = [
            {
                "serial_number": "M66",
                "category": "D1",
                "match_number": "AC38",
                "match_date": date(2020, 8, 9),
                "kickoff_time": datetime(2020, 8, 9, 0, 0),
                "home_team": "六合",
                "away_team": "留萌",
                "studium": "東光スポーツ公園A",
            }
        ]
        self.assertEqual(scraper.schedule_data, expect)
