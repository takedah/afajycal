import re
import sqlite3
import urllib.parse
from datetime import datetime, timedelta, timezone
from afajycal.factory import Factory
from afajycal.logs import DBLog


class Schedule:
    """試合スケジュールを表すハッシュから試合データオブジェクトを作成する。

    Attributes:
        serial_number (str): 連番。
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
        self.__serial_number = kwargs["serial_number"]
        self.__category = kwargs["category"]
        self.__match_number = kwargs["match_number"]
        self.__match_date = kwargs["match_date"]
        self.__kickoff_time = kwargs["kickoff_time"]
        self.__home_team = kwargs["home_team"]
        self.__away_team = kwargs["away_team"]
        self.__studium = kwargs["studium"]
        self.__google_calendar_link = self._make_google_calendar_link()

    @property
    def serial_number(self):
        return self.__serial_number

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


class ScheduleFactory(Factory):
    """Scheduleクラスの配列を生成

    試合スケジュールを表すハッシュのリストからScheduleクラスの配列を生成する。

    Attributes:
        items (:obj:`list` of :obj:`Schedule`): Scheduleクラスのオブジェクトのリスト。

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, row):
        """Scheduleオブジェクトの生成

        Args:
            row (dict): 試合スケジュールを表す辞書データ

        Returns:
            schedule (:obj:`Schedule`): Scheduleクラスのオブジェクト。

        """
        return Schedule(**row)

    def _register_item(self, item):
        """Scheduleオブジェクトをリストへ追加

        Args:
            item (:obj:`Schedule`): Scheduleクラスのオブジェクト。

        """
        self.__items.append(item)


class ScheduleService:
    """試合スケジュールデータを扱う

    """

    def __init__(self, db):
        """
        Args:
            db (:obj:`DB`): データベース操作をラップしたオブジェクト。

        """

        self.__db = db
        self.__table_name = "schedules"
        self.__logger = DBLog()

    def truncate(self):
        """スケジュールテーブルのデータを全削除
        """

        state = "DELETE FROM " + self.__table_name + ";"
        self.__db.execute(state)

    def create(self, schedule):
        """データベースへ試合スケジュールデータを保存

        Args:
            schedule (:obj:`Schedule`): スケジュールデータのオブジェクト

        Returns:
            bool: データの登録が成功したらTrueを返す。

        """

        items = [
            "serial_number",
            "category",
            "match_number",
            "match_date",
            "kickoff_time",
            "home_team",
            "away_team",
            "studium",
        ]

        column_names = ""
        place_holders = ""
        for item in items:
            column_names += "," + item
            place_holders += ",?"

        state = (
            "INSERT OR REPLACE INTO"
            + " "
            + self.__table_name
            + " "
            + "("
            + column_names[1:]
            + ",updated_at"
            + ")"
            + " "
            + "VALUES ("
            + place_holders[1:]
            + ",datetime('now', '+9 hours')"
            + ");"
        )

        values = [
            schedule.serial_number,
            schedule.category,
            schedule.match_number,
            schedule.match_date,
            schedule.kickoff_time,
            schedule.home_team,
            schedule.away_team,
            schedule.studium,
        ]

        try:
            self.__db.execute(state, values)
            return True
        except sqlite3.Error as e:
            self.__logger.error_log(
                self.__table_name, schedule.serial_number, e.args[0]
            )
            return False

    @staticmethod
    def _trim_team_name(team_name):
        """チーム名整形

        データベースに登録されているチーム名が「旭川市立」で始まったり、
        「中学校」、「中」で終わっていないため、チーム名を検索できるよう、
        これらの文字列を削除する。

        Args:
            team_name (str): 元のチーム名。

        Returns:
            trimed_team_name (str): 文字列削除後のチーム名。

        """
        team_name = team_name.strip()
        if re.search(r"^旭川市立", team_name):
            team_name = team_name.replace("旭川市立", "")

        if re.search(r"学校$", team_name):
            team_name = team_name.replace("学校", "")

        if re.search(r"中$", team_name):
            team_name = team_name.replace("中", "")

        trimed_team_name = team_name.strip()
        return trimed_team_name

    def find(self, team_name=None, category=None, match_date=None):
        """対象のチーム・カテゴリの試合スケジュールを返す。

        Args:
            team_name(str, optional): 対象のチーム名。デフォルトはNone。
            category(str, optional): 対象のカテゴリ名。デフォルトはNone。
            match_date(:obj:`datetime.date`, optional): 基準の日時。デフォルトはNone。

        Returns:
            res (list of :obj:`Schedule`): 検索結果。

        """
        if team_name is None:
            team_name = "%"
        else:
            team_name = "%" + self._trim_team_name(team_name) + "%"
        if category is None:
            category = "%"
        else:
            category = "%" + category + "%"
        search_condition = (
            "WHERE"
            + " "
            + "(home_team LIKE ? OR away_team LIKE ?)"
            + " "
            + "AND category LIKE ?"
        )
        search_values = [team_name, team_name, category]
        if match_date is not None:
            search_condition += " " + "AND match_date = ?"
            search_values.append(match_date)
        self.__db.execute(
            "SELECT"
            + " "
            + "id,serial_number,category,match_number,match_date,kickoff_time,"
            + "home_team,away_team,studium"
            + " "
            + "FROM"
            + " "
            + self.__table_name
            + " "
            + search_condition
            + " "
            + "ORDER BY kickoff_time ASC;",
            search_values,
        )
        factory = ScheduleFactory()
        for row in self.__db.fetchall():
            factory.create(row)
        return factory.items

    def get_all_teams(self):
        """試合スケジュールのある全てのチーム名を返す。

        Returns:
            team_names (list): チーム名のリスト。

        """
        team_names = list()
        self.__db.execute("SELECT home_team FROM " + self.__table_name + ";")
        home_team_rows = self.__db.fetchall()
        self.__db.execute("SELECT away_team FROM " + self.__table_name + ";")
        away_team_rows = self.__db.fetchall()
        for row in home_team_rows:
            team_names.append(row["home_team"])
        for row in away_team_rows:
            team_names.append(row["away_team"])

        team_names = list(filter(lambda a: a != "", team_names))
        return sorted(set(team_names), key=team_names.index)

    def get_all_categories(self):
        """全てのカテゴリ名を返す。

        Returns:
            categories (list): カテゴリ名のリスト。

        """
        categories = list()
        self.__db.execute("SELECT DISTINCT category FROM " + self.__table_name + ";")
        for row in self.__db.fetchall():
            categories.append(row["category"])
        return list(filter(lambda a: a != "", categories))

    def get_last_updated(self):
        """テーブルの最終更新日を返す。

        Returns:
            last_updated (:obj:`datetime.datetime'): scheduleテーブルのupdatedカラムで一番最新の値を返す。
        """
        self.__db.execute(
            "SELECT max(updated_at),updated_at FROM " + self.__table_name + ";"
        )
        row = self.__db.fetchone()
        if row["max(updated_at)"] is None:
            return None
        else:
            return datetime.strptime(row["max(updated_at)"], "%Y-%m-%d %H:%M:%S")
