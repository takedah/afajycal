import numpy as np
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
from requests import Timeout, HTTPError
from afajycal.config import Config


class HTMLDownloadError(Exception):
    pass


class DownloadedHTML:
    """試合スケジュールHTMLページのダウンロード

    旭川地区サッカー協会第3種委員会Webサイトから試合スケジュールのページを
    ダウンロードしてデータに変換する。

    Attributes:
        content (str): 試合スケジュールページのHTMLファイルの文字列データ

    """

    def __init__(self, afa_url):
        """
        Args:
            afa_url (str): 試合スケジュールWebページのURL

        """

        self.__afa_url = afa_url
        self.__content = ""
        self._get_html_content()

    @property
    def content(self):
        return self.__content

    def _get_html_content(self):
        """旭川地区サッカー協会第3種委員会WebサイトからHTMLファイルの文字列データを取得する。
        """
        try:
            response = requests.get(self.__afa_url)
        except (ConnectionError, Timeout, HTTPError):
            raise HTMLDownloadError("cannot connect to web server.")
        if response.status_code != 200:
            raise HTMLDownloadError("cannot get HTML contents.")
        self.__content = response.content


class DownloadedExcel:
    """試合スケジュールExcelファイルのダウンロード

    旭川地区サッカー協会第3種委員会Webサイトから試合スケジュールのExcelを
    ダウンロードしてデータに変換する。

    Attributes:
        lists (list of list): 試合スケジュールExcelファイルの二次元配列データ

    """

    def __init__(self, afa_url):
        """
        Args:
            afa_url (str): 試合スケジュール excelファイルのURL

        """

        self.__afa_url = afa_url
        self.__lists = ""
        self._get_worksheet_lists()

    @property
    def lists(self):
        return self.__lists

    @property
    def _afa_url(self):
        return self.__afa_url

    def _get_worksheet_lists(self):
        """Excelファイルから二次元配列を抽出
        """

        df = pd.read_excel(
            self.__afa_url,
            sheet_name="日程順",
            header=None,
            index_col=None,
            skiprows=range(1),
            dtype=str,
        )
        df.replace(np.nan, "", inplace=True)
        self.__lists = df.values.tolist()


class ScrapedData:
    @staticmethod
    def get_month(month_str):
        """月を表す文字列を数値に変換する。

        Args:
            month_str (str): 月を表す文字列。

        Returns:
            month (int): 数値。

        """
        if re.search(r"^[0-9]{1,2}$", month_str):
            month = int(month_str)
            if month < 1 or 12 < month:
                month = 1
        else:
            month = 1
        return month

    @staticmethod
    def get_day(day_str):
        """日を表す文字列を数値に変換する。

        Args:
            day_str (str): 日を表す文字列。

        Returns:
            day (int): 数値。

        """
        if re.search(r"^[0-9]{1,2}$", day_str):
            day = int(day_str)
            if day < 1 or 31 < day:
                day = 1
        else:
            day = 1
        return day

    @staticmethod
    def get_time(time_str):
        """時間・分を表す文字列を数値に変換する。

        Args:
            str (str): 時間・分を表す文字列。

        Returns:
            time (list): 時間・分を数値で格納した配列。

        Raises:
            ValueError: 時間・分を表すのに適切ではない数値だった場合。

        """
        if re.search(r"^[0-9]{1,2}:[0-9]{2}", time_str):
            tmp = time_str.split(":")
            hour = int(tmp[0])
            minute = int(tmp[1])
            if hour < 0 or 24 < hour:
                hour = 0
            if minute < 0 or 59 < minute:
                hour = 0
        else:
            hour = 0
            minute = 0
        return [hour, minute]

    @staticmethod
    def get_valid_year(month, year):
        """試合スケジュールの月が1月から3月までの間だった場合、年を1加算して補正する。

        Args:
            month (int): 月。
            year (int): 年。

        Returns:
            valid_year (int): 補正後の年。

       """
        if month < 4:
            return year + 1
        else:
            return year


class ScrapedHTMLData(ScrapedData):
    """試合スケジュールデータ抽出

    旭川地区サッカー協会第3種委員会WebサイトからダウンロードしたHTMLから、
    試合スケジュールデータを抽出し、リストを生成する。

    Attributes:
        schedule_data (list of dict): 試合スケジュールを表すハッシュのリスト。

    """

    def __init__(self, downloaded_html):
        """
        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードした
                試合スケジュールHTMLを要素に持つオブジェクト。

         """
        self.__downloaded_html = downloaded_html
        self.__this_year = Config.THIS_YEAR
        self.__JST = Config.JST
        self.__schedule_data = list()
        for row in self._get_table_values():
            if self._extract_schedule_data(row):
                self.__schedule_data.append(self._extract_schedule_data(row))

    @property
    def schedule_data(self):
        return self.__schedule_data

    def _get_table_values(self):
        """試合スケジュールHTMLからtableの内容を抽出して二次元配列に格納する。

        Returns:
            table_values (list of list): tableの内容で構成される二次元配列。

        """
        soup = BeautifulSoup(self.__downloaded_html.content, "html.parser")
        table_values = list()
        for table in soup.find_all("table", attrs={"border": "1"}):
            for tr in table.find_all("tr"):
                row = list()
                val = ""
                for td in tr.find_all("td"):
                    if td.string is None:
                        val = ""
                    else:
                        val = td.string.strip()
                    row.append(val)
                table_values.append(row)
        return table_values

    def _extract_schedule_data(self, row):
        """試合スケジュールデータへの変換

        試合スケジュールHTMLのtable要素から抽出した二次元配列の要素となる配列
        （列の配列）を試合スケジュールを表すハッシュに変換する。

        Args:
            row (list): 試合スケジュールの配列

        Returns:
            schedule_data (dict or bool): 試合スケジュールを表すハッシュ

        """
        # 見出しの列はスキップ。
        if row == [
            "",
            "M.No.",
            "節",
            "月",
            "日",
            "C",
            "G",
            "会場",
            "KO",
            "HOME",
            "",
            "AWAY",
        ]:
            return False
        # 連番のない列もスキップ。
        if row[0] == "":
            return False

        month = self.get_month(row[3])
        day = self.get_day(row[4])
        time = self.get_time(row[8])
        year = self.get_valid_year(month, self.__this_year)
        return {
            "serial_number": row[0],
            "category": row[5],
            "match_number": row[1],
            "match_date": date(year, month, day),
            "kickoff_time": datetime(
                year, month, day, time[0], time[1], tzinfo=self.__JST
            ),
            "home_team": row[9].replace("\u3000", ""),
            "away_team": row[11].replace("\u3000", ""),
            "studium": row[7],
        }


class ScrapedExcelData(ScrapedData):
    """試合スケジュールデータ抽出

    旭川地区サッカー協会第3種委員会WebサイトからダウンロードしたExcelファイルから、
    試合スケジュールデータを抽出し、リストを生成する。

    Attributes:
        schedule_data (list of dict): 試合スケジュールを表すハッシュのリスト。

    """

    def __init__(self, downloaded_excel):
        """
        Args:
            downloaded_excel (:obj:`DownloadedExcel`): ダウンロードした
                試合スケジュールExcelデータを要素に持つオブジェクト。

         """
        self.__this_year = Config.THIS_YEAR
        self.__JST = Config.JST
        self.__schedule_data = list()
        for row in downloaded_excel.lists:
            if self._extract_schedule_data(row):
                self.__schedule_data.append(self._extract_schedule_data(row))

    @property
    def schedule_data(self):
        return self.__schedule_data

    def _extract_schedule_data(self, row):
        """試合スケジュールデータへの変換

        試合スケジュールHTMLのtable要素から抽出した二次元配列の要素となる配列
        （列の配列）を試合スケジュールを表すハッシュに変換する。

        Args:
            row (list): 試合スケジュールの配列

        Returns:
            schedule_data (dict or bool): 試合スケジュールを表すハッシュ

        """
        # 連番のない列、日付が入っていない列はスキップ。
        if row[0] == "" or row[3] == "" or row[4] == "":
            return False

        month = self.get_month(row[3])
        day = self.get_day(row[4])
        time = self.get_time(row[8])
        year = self.get_valid_year(month, self.__this_year)
        return {
            "serial_number": row[0],
            "category": row[5],
            "match_number": row[1],
            "match_date": date(year, month, day),
            "kickoff_time": datetime(
                year, month, day, time[0], time[1], tzinfo=self.__JST
            ),
            "home_team": row[9].replace("\u3000", ""),
            "away_team": row[11].replace("\u3000", ""),
            "studium": row[7],
        }
