import re
from datetime import date, datetime, timedelta, timezone
import requests
from requests import Timeout, HTTPError
from bs4 import BeautifulSoup
from afajycal.config import Config


class HTMLDownloadError(Exception):
    pass


class Scraper:
    """
    旭川地区サッカー協会第3種委員会Webサイトから試合スケジュールデータを
    抽出する。

    Attributes
    ----------
    url : str
        旭川地区サッカー協会第3種委員会WebサイトのURL。
    year : int
        対象年度。
    JST : timezone
        日本時間のtimezoneオブジェクト。

    """

    def __init__(self):
        self.afa_url = Config.AFA_URL
        self.this_year = Config.THIS_YEAR
        self.JST = timezone(timedelta(hours=+9), "JST")

    def _download_html_content(self):
        """
        対象URLのHTMLファイルをダウンロードして返す。

        Returns
        -------
        html_content : bytes
            HTMLコンテンツ。ダウンロードに失敗したらNoneを返す。

        """
        try:
            response = requests.get(self.afa_url)
        except (ConnectionError, Timeout, HTTPError):
            return None

        if response.status_code != 200:
            return None

        html_content = response.content
        return html_content

    def _html_to_list(self):
        """
        HTMLコンテンツから試合スケジュールの書かれたtableの内容のみ配列に
        格納する。

        Returns
        -------
        data : list
            table要素の内容を行ごとに二次元配列に格納したもの。

        """
        html_content = self._download_html_content()
        if html_content is None:
            raise HTMLDownloadError("cannot get HTML content.")

        soup = BeautifulSoup(html_content, "html.parser")
        if soup.find("table", attrs={"border": "1"}) is None:
            return []

        data = list()
        for table in soup.find_all("table", attrs={"border": "1"}):
            for tr in table.find_all("tr"):
                tmp = list()
                val = ""
                for td in tr.find_all("td"):
                    if td.string is None:
                        val = ""
                    else:
                        val = td.string
                    tmp.append(val)

                # delete header line.
                if tmp != [
                    "No.",
                    "",
                    "",
                    "M.No.",
                    "節",
                    "月",
                    "日",
                    "G",
                    "会場",
                    "KO",
                    "HOME",
                    "",
                    "AWAY",
                ]:
                    data.append(tmp)

        return data

    @staticmethod
    def _get_month(month_str):
        """
        月を表す文字列を数値に変換する。

        Parameters
        ----------
        month_str : str
            月を表す文字列。

        Returns
        -------
        month : int
            数値。月を表すのに適切ではない数値だった場合、1を返す。

        """
        month = 0
        if re.search(r"^[0-9]{1,2}$", month_str):
            month = int(month_str)
            if month < 1 or 12 < month:
                month = 1
        else:
            month = 1

        return month

    @staticmethod
    def _get_day(day_str):
        """
        日を表す文字列を数値に変換する。

        Parameters
        ----------
        day_str : str
            日を表す文字列。日を表すのに適切ではない数値だった場合、1を返す。

        Returns
        -------
        day : int
            数値。

        """
        day = 0
        if re.search(r"^[0-9]{1,2}$", day_str):
            day = int(day_str)
            if day < 1 or 31 < day:
                day = 1
        else:
            day = 1

        return day

    @staticmethod
    def _get_time(time_str):
        """
        時間・分を表す文字列を数値に変換する。

        Parameters
        ----------
        str : str
            時間・分を表す文字列。

        Returns
        -------
        time : list
            時間・分を数値で格納した配列。時間・分を表すのに適切ではない
            数値だった場合、配列のそれぞれの値は0とする。

        """
        time = list()
        if re.search(r"^[0-9]{1,2}:[0-9]{2}$", time_str):
            tmp = time_str.split(":")
            hour = int(tmp[0])
            minute = int(tmp[1])
            if hour < 0 or 24 < hour:
                hour = 0
            if minute < 0 or 59 < minute:
                minute = 0
            time = [hour, minute]
        else:
            time = [0, 0]

        return time

    @staticmethod
    def _get_valid_year(month, year):
        """
        試合スケジュールの月が1月から3月までの間だった場合、年を1加算して
        補正する。

        Parameters
        ----------
        month : int
            月。
        year : int
            年。

        Returns
        -------
        valid_year : int
            補正後の年。

        """
        if 3 < month:
            valid_year = year
        else:
            valid_year = year + 1

        return valid_year

    def get_schedule_list(self):
        """
        旭川地区サッカー協会第3種委員会Webサイトから試合スケジュールデータを
        抽出する。

        Returns
        -------
        schedule_list : list of dicts
            試合スケジュールデータ。
            データ配列は次の要素で構成される。
            連番、カテゴリ、試合番号、試合開始日時、ホームチーム名、
            アウェイチーム名、試合会場

        """
        schedule_list = list()
        for item in self._html_to_list():
            if not item[0] == "":
                tmp = dict()
                month = self._get_month(item[5])
                day = self._get_day(item[6])
                time = self._get_time(item[9])
                year = self._get_valid_year(month, self.this_year)
                tmp = {
                    "number": int(item[0]),
                    "category": item[1],
                    "match_number": item[3],
                    "match_date": date(year, month, day),
                    "kickoff_time": datetime(
                        year, month, day, time[0], time[1], tzinfo=self.JST
                    ),
                    "home_team": item[10].replace("\u3000", ""),
                    "away_team": item[12].replace("\u3000", ""),
                    "studium": item[8],
                }
                schedule_list.append(tmp)

        return schedule_list
