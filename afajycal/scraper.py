import re
from datetime import datetime, timedelta, timezone
import requests
from requests import Timeout, HTTPError
from bs4 import BeautifulSoup
from afajycal.config import Config


class HTMLDownloadError(Exception):
    pass


class Scraper:
    """
    get junior youth soccer match schedule data from AOSC Web site.

    Attributes
    ----------
    url : str
        AOSC web site's URL where the junior youth soccer match schedule
        in Asahikawa is written.
    year : int
        target year.
    JST : timezone
        timezone of Asahikawa, Japan.
    """

    def __init__(self):
        self.afa_url = Config.AOSC_URL
        self.this_year = Config.THIS_YEAR
        self.JST = timezone(timedelta(hours=+9), 'JST')

    def _download_html_content(self):
        """
        download HTML file from AOSC Web site where
        the junior youth soccer match schedule in Asahikawa
        is written.

        Returns
        -------
        html_content : bytes
        html contents. If some errors occured in requests,
        this method returns None.
        """
        try:
            response = requests.get(self.afa_url)
        except(ConnectionError, Timeout, HTTPError):
            return None

        if response.status_code != 200:
            return None

        html_content = response.content
        return html_content

    def _html_to_list(self):
        """
        extract table element from HTML file in AOSC Web site
        where the junior youth soccer match schedule in Asahikawa
        is written.

        Returns
        -------
        data : list
            a list extracted from this URL which the junior youth soccer
            match schedule is written.
            if downloaded HTML content doesn't have table which is written
            match suchedule, this method returns empty list.
        """
        html_content = self._download_html_content()
        if html_content is None:
            raise HTMLDownloadError('cannot get HTML content.')

        soup = BeautifulSoup(html_content, 'html.parser')
        if soup.find('table', attrs={'border': '1'}) is None:
            return []

        data = list()
        for table in soup.find_all('table', attrs={'border': '1'}):
            for tr in table.find_all('tr'):
                tmp = list()
                val = ''
                for td in tr.find_all('td'):
                    if td.string is None:
                        val = ''
                    else:
                        val = td.string
                    tmp.append(val)

                # delete header line.
                if tmp != [
                        'No.', '', '', 'M.No.', '節', '月', '日',
                        'G', '会場', 'KO', 'HOME', '', 'AWAY']:
                    data.append(tmp)

        return data

    @staticmethod
    def _get_month(str):
        """
        change string to integer of month.

        Parameters
        ----------
        str : str
            string of month number.

        Returns
        -------
        month : int
            integer of month.
        """

        month = 0
        if re.search(r'^[0-9]{1,2}$', str):
            month = int(str)
            if month < 1 or 12 < month:
                month = 1
        else:
            month = 1

        return month

    @staticmethod
    def _get_day(str):
        """
        change string to integer of day.

        Parameters
        ----------
        str : str
            string of day number.

        Returns
        -------
        day : int
            integer of day.
        """

        day = 0
        if re.search(r'^[0-9]{1,2}$', str):
            day = int(str)
            if day < 1 or 31 < day:
                day = 1
        else:
            day = 1

        return day

    @staticmethod
    def _get_time(str):
        """
        change string to integer of time.

        Parameters
        ----------
        str : str
            string of time.

        Returns
        -------
        time : list
            list includes integer of hour and minute.
        """

        time = list()
        if re.search(r'^[0-9]{1,2}:[0-9]{2}$', str):
            tmp = str.split(':')
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
        if the month is between 1 and 3, add 1 to the year.

        Parameters
        ----------
        month : int
            month number.
        year : int
            year number.

        Returns
        -------
        valid_year : int
            integer of month.
        """

        if 3 < month:
            valid_year = year
        else:
            valid_year = year + 1

        return valid_year

    def get_schedule_list(self):
        """
        get junior youth soccer match schedule data which extracted from
        HTML file in AOSC Web site.

        Returns
        -------
        schedule_list : list of dicts
            a list includes dict data which is match schedule.
            these dicts have data below.
            number, division, match_group,
            match_number, match_date, kickoff_time,
            home_team, away_team, studium.
        """
        schedule_list = list()
        for item in self._html_to_list():
            tmp = dict()
            month = self._get_month(item[5])
            day = self._get_day(item[6])
            time = self._get_time(item[9])
            year = self._get_valid_year(month, self.this_year)
            tmp = {
                    'number': int(item[0]),
                    'category': item[1],
                    'match_number': item[3],
                    'kickoff_time': datetime(
                        year, month, day, time[0], time[1], tzinfo=self.JST),
                    'home_team': item[10].replace('\u3000', ''),
                    'away_team': item[12].replace('\u3000', ''),
                    'studium': item[8]}
            schedule_list.append(tmp)

        return schedule_list
