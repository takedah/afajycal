import re
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import psycopg2
from psycopg2.extras import DictCursor

from afajycal.config import Config
from afajycal.errors import DatabaseError, DataError
from afajycal.logs import AppLog
from afajycal.models import Schedule, ScheduleFactory


class ScheduleService:
    """試合スケジュールデータを扱う"""

    def __init__(self, db):
        """
        Args:
            db (:obj:`DB`): データベース操作をラップしたオブジェクト。

        """

        self.__cursor = db.cursor()
        self.__table_name = "schedules"
        self.__JST = Config.JST
        self.__logger = AppLog()

    def _execute(self, sql: str, parameters: tuple = None) -> bool:
        """DictCursorオブジェクトのexecuteメソッドのラッパー。

        Args:
            sql (str): SQL文
            parameters (tuple): SQLにプレースホルダを使用する場合の値を格納したリスト

        """
        try:
            if parameters:
                self.__cursor.execute(sql, parameters)
            else:
                self.__cursor.execute(sql)
            return True
        except (
            psycopg2.DataError,
            psycopg2.IntegrityError,
            psycopg2.InternalError,
        ) as e:
            raise DataError(e.args[0])

    def _fetchone(self) -> DictCursor:
        """DictCursorオブジェクトのfetchoneメソッドのラッパー。

        Returns:
            results (:obj:`DictCursor`): 検索結果のイテレータ

        """
        return self.__cursor.fetchone()

    def _fetchall(self):
        """DictCursorオブジェクトのfetchallメソッドのラッパー。

        Returns:
            results (list of :obj:`DictCursor`): 検索結果のイテレータのリスト

        """
        return self.__cursor.fetchall()

    def _get_objects(self) -> list:
        """検索結果から試合スケジュールデータのリストを作成する。

        Returns:
            locations (list of obj:`Schedule`): 検索結果のイテレータオブジェクトのリスト

        """
        results = self._fetchall()
        factory = ScheduleFactory()
        for row in results:
            factory.create(**row)
        return factory.items

    def _info_log(self, message) -> None:
        """AppLogオブジェクトのinfoメソッドのラッパー。

        Args:
            message (str): 通常のログメッセージ
        """
        return self.__logger.info(message)

    def _error_log(self, message) -> None:
        """AppLogオブジェクトのerrorメソッドのラッパー。

        Args:
            message (str): エラーログメッセージ

        """
        return self.__logger.error(message)

    def truncate(self) -> None:
        """スケジュールテーブルのデータを全削除"""

        state = "TRUNCATE TABLE " + self.__table_name + " RESTART IDENTITY;"
        self._execute(state)
        self._info_log(self.__table_name + "テーブルを初期化しました。")

    def create(self, schedule: Schedule) -> bool:
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
            "updated_at",
        ]

        column_names = ""
        place_holders = ""
        upsert = ""
        for item in items:
            column_names += "," + item
            place_holders += ",%s"
            upsert += "," + item + "=%s"

        state = (
            "INSERT INTO"
            + " "
            + self.__table_name
            + " "
            + "("
            + column_names[1:]
            + ")"
            + " "
            + "VALUES ("
            + place_holders[1:]
            + ")"
            + " "
            + "ON CONFLICT(serial_number)"
            + " "
            + "DO UPDATE SET"
            + " "
            + upsert[1:]
        )

        temp_values = [
            schedule.serial_number,
            schedule.category,
            schedule.match_number,
            schedule.match_date,
            schedule.kickoff_time,
            schedule.home_team,
            schedule.away_team,
            schedule.studium,
            datetime.now(timezone(timedelta(hours=+9))),
        ]
        # UPDATE句用にリストを重複させる。
        values = tuple(temp_values + temp_values)

        try:
            self._execute(state, values)
            return True
        except (DatabaseError, DataError) as e:
            self._error_log(e.message)
            return False

    @staticmethod
    def _trim_team_name(team_name: str) -> str:
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

    def find(
        self,
        team_name: str = None,
        category: str = None,
        match_date: date = None,
    ) -> list:
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
            + "(home_team LIKE %s OR away_team LIKE %s)"
            + " "
            + "AND category LIKE %s"
        )
        search_values = (team_name, team_name, category)
        if match_date is not None:
            search_condition += " " + "AND match_date = %s"
            search_values = (search_values) + (match_date,)
        self._execute(
            "SELECT"
            + " "
            + "serial_number,category,match_number,match_date,kickoff_time,"
            + "home_team,away_team,studium"
            + " "
            + "FROM"
            + " "
            + self.__table_name
            + " "
            + search_condition
            + " "
            + "ORDER BY kickoff_time DESC;",
            search_values,
        )
        return self._get_objects()

    def get_all_teams(self) -> list:
        """試合スケジュールのある全てのチーム名を返す。

        Returns:
            team_names (list): チーム名のリスト。

        """
        team_names = list()
        self._execute("SELECT home_team FROM " + self.__table_name + ";")
        home_team_rows = self._fetchall()
        self._execute("SELECT away_team FROM " + self.__table_name + ";")
        away_team_rows = self._fetchall()
        for row in home_team_rows:
            team_names.append(row["home_team"])
        for row in away_team_rows:
            team_names.append(row["away_team"])

        team_names = list(filter(lambda a: a != "", team_names))
        return sorted(set(team_names), key=team_names.index)

    def get_all_categories(self) -> list:
        """全てのカテゴリ名を返す。

        Returns:
            categories (list): カテゴリ名のリスト。

        """
        categories = list()
        self._execute("SELECT DISTINCT category FROM " + self.__table_name + ";")
        for row in self._fetchall():
            categories.append(row["category"])
        categories = list(filter(lambda a: a != "", categories))
        return sorted(set(categories))

    def get_last_updated(self) -> Optional[datetime]:
        """テーブルの最終更新日を返す。

        Returns:
            last_updated (:obj:`datetime.datetime'): scheduleテーブルのupdatedカラムで一番最新の値を返す。
        """
        self._execute("SELECT max(updated_at) FROM " + self.__table_name + ";")
        row = self._fetchone()
        if row["max"] is None:
            return None
        else:
            return row["max"]
