import urllib.parse
from datetime import timedelta, timezone
from abc import ABCMeta, abstractmethod


class Schedule:
    """試合スケジュールを表すハッシュから試合データオブジェクトを作成する。

    Attributes:
        number (str): 連番。
        category (str): 試合カテゴリ。
        match_number (str): 試合番号。
        kickoff_time (datetime.date): 試合開始時刻。
        home_team (str): ホームチーム。
        away_team (str): アウェイチーム。
        studium (str): 試合会場。
        google_calendar_link (str): 試合スケジュールをGoogleカレンダーへ追加するリンク。

    """

    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: 試合スケジュールを表すハッシュ。

        """
        self.__number = kwargs["number"]
        self.__category = kwargs["category"]
        self.__match_number = kwargs["match_number"]
        self.__match_date = kwargs["match_date"]
        self.__kickoff_time = kwargs["kickoff_time"]
        self.__home_team = kwargs["home_team"]
        self.__away_team = kwargs["away_team"]
        self.__studium = kwargs["studium"]
        self.__google_calendar_link = self._make_google_calendar_link()

    @property
    def number(self):
        return self.__number

    @property
    def category(self):
        return self.__category

    @property
    def match_number(self):
        return self.__match_number

    @property
    def match_date(self):
        return self.__match_date

    @property
    def kickoff_time(self):
        return self.__kickoff_time

    @property
    def home_team(self):
        return self.__home_team

    @property
    def away_team(self):
        return self.__away_team

    @property
    def studium(self):
        return self.__studium

    @property
    def google_calendar_link(self):
        return self.__google_calendar_link

    def _make_google_calendar_link(self):
        """googleカレンダーに追加できるURLを生成する。

        Returns:
            str: googleカレンダー追加用URL。

        """
        title = self.category + " (" + self.home_team + " vs " + self.away_team + ")"
        start_date = self.kickoff_time.astimezone(timezone.utc)
        if self.category == "サテライト":
            game_time = 60
        else:
            game_time = 90
        end_date = start_date + timedelta(minutes=game_time)
        return (
            "https://www.google.com/calendar/event?"
            + "action="
            + "TEMPLATE"
            + "&text="
            + urllib.parse.quote(title)
            + "&location="
            + urllib.parse.quote(self.studium)
            + "&dates="
            + start_date.strftime("%Y%m%dT%H%M%SZ")
            + "/"
            + end_date.strftime("%Y%m%dT%H%M%SZ")
        )


class Factory(metaclass=ABCMeta):
    @abstractmethod
    def _create_schedule(self, match_data):
        pass

    @abstractmethod
    def _register_schedule(self, schedule):
        pass

    def create(self, match_data):
        schedule = self._create_schedule(match_data)
        self._register_schedule(schedule)
        return schedule


class ScheduleFactory(Factory):
    """Scheduleクラスの配列を生成

    試合スケジュールを表すハッシュのリストからScheduleクラスの配列を生成する。

    Attributes:
        schedules (:obj:`list` of :obj:`Schedule`): Scheduleクラスのオブジェクトのリスト。

    """

    def __init__(self):
        self.__schedules = list()

    @property
    def schedules(self):
        return self.__schedules

    def _create_schedule(self, match_data):
        """Scheduleオブジェクトの生成

        Args:
            match_data (dict): 試合スケジュールを表す辞書データ

        Returns:
            schedule (:obj:`Schedule`): Scheduleクラスのオブジェクト。

        """
        return Schedule(**match_data)

    def _register_schedule(self, schedule):
        """Scheduleオブジェクトをリストへ追加

        Args:
            schedule (:obj:`Schedule`): Scheduleクラスのオブジェクト。

        """
        self.__schedules.append(schedule)
