import urllib.parse
from datetime import date, datetime, timedelta, timezone

from afajycal.errors import ScheduleError
from afajycal.factory import Factory


class Schedule:
    """試合スケジュールを表すハッシュから試合データオブジェクトを作成する。

    Attributes:
        serial_number (str): 連番。
        category (str): 試合カテゴリ。
        match_number (str): 試合番号。
        match_date (datetime.date): 試合開始日。
        kickoff_time (datetime.date): 試合開始時刻。
        home_team (str): ホームチーム。
        away_team (str): アウェイチーム。
        studium (str): 試合会場。
        google_calendar_link (str): 試合スケジュールをGoogleカレンダーへ追加するリンク。

    """

    def __init__(
        self,
        serial_number: str,
        category: str,
        match_number: str,
        match_date: date,
        kickoff_time: datetime,
        home_team: str,
        away_team: str,
        studium: str,
    ):
        """
        Args:
            serial_number (str): 連番。
            category (str): 試合カテゴリ。
            match_number (str): 試合番号。
            match_date (datetime.date): 試合開始日。
            kickoff_time (datetime.datetime): 試合開始時刻。
            home_team (str): ホームチーム。
            away_team (str): アウェイチーム。
            studium (str): 試合会場。
            google_calendar_link (str): 試合スケジュールをGoogleカレンダーへ追加するリンク。

        """
        self.__serial_number = serial_number
        self.__category = category
        self.__match_number = match_number
        if isinstance(match_date, date):
            self.__match_date = match_date
        else:
            raise ScheduleError("試合開始日が正しくありません。")
        if isinstance(kickoff_time, datetime):
            self.__kickoff_time = kickoff_time
        else:
            raise ScheduleError("試合開始時刻が正しくありません。")
        self.__home_team = home_team
        self.__away_team = away_team
        self.__studium = studium
        self.__google_calendar_link = self._make_google_calendar_link()

    @property
    def serial_number(self) -> str:
        return self.__serial_number

    @property
    def category(self) -> str:
        return self.__category

    @property
    def match_number(self) -> str:
        return self.__match_number

    @property
    def match_date(self) -> date:
        return self.__match_date

    @property
    def kickoff_time(self) -> datetime:
        return self.__kickoff_time

    @property
    def home_team(self) -> str:
        return self.__home_team

    @property
    def away_team(self) -> str:
        return self.__away_team

    @property
    def studium(self) -> str:
        return self.__studium

    @property
    def google_calendar_link(self) -> str:
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


class ScheduleFactory(Factory):
    """試合スケジュールモデルを生成

    試合スケジュールを表すハッシュのリストからScheduleクラスのリストを生成する。

    Attributes:
        items (:obj:`list` of :obj:`Schedule`): Scheduleクラスのオブジェクトのリスト。

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self) -> list:
        return self.__items

    def _create_item(self, **row) -> Schedule:
        """Scheduleオブジェクトの生成

        Args:
            row (dict): 試合スケジュールデータオブジェクトを作成するための引数。

        Returns:
            schedule (:obj:`Schedule`): Scheduleクラスのオブジェクト。

        """
        return Schedule(**row)

    def _register_item(self, item: Schedule):
        """Scheduleオブジェクトをリストへ追加

        Args:
            item (:obj:`Schedule`): Scheduleクラスのオブジェクト。

        """
        self.__items.append(item)
