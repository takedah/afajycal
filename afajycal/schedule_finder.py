import re
from afajycal.match_data import MatchData
from afajycal.config import Config


class ScheduleFinder(MatchData):
    """旭川地区サッカー協会第3種試合スケジュール

    旭川地区サッカー協会第3種事業委員会Webサイトから試合スケジュールを取得し、
    試合スケジュールのリストを要素に持つ。

    Attributes:
        match_data (list of dict): 試合スケジュールを表すディクショナリのリスト。

    """

    def __init__(self, db):
        """
        Args:
            db (:obj:`DB`): データベース操作をラップしたオブジェクト。

        """
        self.__db = db
        self.__table_name = Config.TABLE
        self.__match_data = list()

    @property
    def match_data(self):
        return self.__match_data

    def _cursor(self):
        """データベースのカーソルオブジェクトを返すラッパーメソッド。

        Returns:
            cursor (:obj:'sqlite3.Cursor'): Cursorオブジェクト。

        """
        return self.__db.cursor()

    def _get_datetime(self, datetime_str):
        return self.__db.get_datetime(datetime_str)

    def _get_date(self, date_str):
        return self.__db.get_date(date_str)

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

    def find(self, args: dict):
        """対象のチーム・カテゴリの試合スケジュールを返す。

        Args:
            args["team_name"] (str, optional): 対象のチーム名。デフォルトはNone。
            args["category"] (str, optional): 対象のカテゴリ名。デフォルトはNone。
            args["match_date"] (:obj:`datetime.date`, optional): 基準の日時。デフォルトはNone。

        """
        team_name = args.get("team_name", None)
        category = args.get("category", None)
        match_date = args.get("match_date", None)
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
        cur = self._cursor()
        cur.execute(
            "SELECT"
            + " "
            + "id,number,category,match_number,match_date,kickoff_time,"
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
        res = list()
        for row in cur.fetchall():
            row["match_date"] = self._get_date(row["match_date"])
            row["kickoff_time"] = self._get_datetime(row["kickoff_time"])
            res.append(row)
        self.__match_data = res
        return self
