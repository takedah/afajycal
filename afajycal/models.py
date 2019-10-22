import urllib.parse
from datetime import datetime, timedelta, timezone


class MatchSchedule:
    """
    試合スケジュールを表す。

    Attributes
    ----------
    number : int
        試合番号。
    category : str
        試合カテゴリ。
    match_number : str
        試合カテゴリごとの連番。
    match_date : date
        試合日。
    kickoff_time : datetime
        試合開始日時。
    home_team : str
        ホームチーム名。
    away_team : str
        アウェイチーム名。
    studium : str
        試合会場。

    """

    def __init__(self, **kwargs):
        self.number = kwargs["number"]
        self.category = kwargs["category"]
        self.match_number = kwargs["match_number"]
        self.match_date = kwargs["match_date"]
        self.kickoff_time = self.get_datetime(kwargs["kickoff_time"])
        self.home_team = kwargs["home_team"]
        self.away_team = kwargs["away_team"]
        self.studium = kwargs["studium"]

    @staticmethod
    def get_datetime(datetime_str):
        """
        SQLite3が返す文字列の日時をdatetimeオブジェクトに変換する。

        Parameters
        ----------
        datetime_str : str
            SQLite3が返す文字列の日時。
            %Y-%m-%d %H:%M:%S + 時差

        Returns
        -------
        datetime_object : datetime
            datetimeオブジェクト。

        """
        base_datetime = datetime_str[:19]
        time_difference = datetime_str[-6:].replace(":", "")
        return datetime.strptime(base_datetime + time_difference, "%Y-%m-%d %H:%M:%S%z")

    def kickoff(self):
        """
        キックオフ日時を文字列に変換して返す。

        Returns
        -------
        kickoff_datetime : str
            キックオフ日時の文字列。

        """
        return self.kickoff_time.strftime("%Y/%m/%d %a %H:%M")

    def google_calendar_link(self):
        """
        試合スケジュールをgoogleカレンダーに追加できるURLを生成する。

        Returns
        -------
        link : str
            googleカレンダー追加用URL。

        """
        title = self.category + " (" + self.home_team + " vs " + self.away_team + ")"
        start_date = self.kickoff_time.astimezone(timezone.utc)
        if self.category == "サテライト":
            game_time = 60
        else:
            game_time = 90

        end_date = start_date + timedelta(minutes=game_time)
        start_date_str = start_date.strftime("%Y%m%dT%H%M%SZ")
        end_date_str = end_date.strftime("%Y%m%dT%H%M%SZ")
        link = (
            "https://www.google.com/calendar/event?"
            + "action="
            + "TEMPLATE"
            + "&text="
            + urllib.parse.quote(title)
            + "&location="
            + urllib.parse.quote(self.studium)
            + "&dates="
            + start_date_str
            + "/"
            + end_date_str
        )
        return link
