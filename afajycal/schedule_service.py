from datetime import datetime
from afajycal.config import Config


class ScheduleService:
    """Web表示に使うパーツ関係をまとめたクラス

    試合スケジュールのデータベースからWeb表示に必要なパーツを返す処理をまとめたもの。

    """

    def __init__(self, db):
        """
        Args:
            db (:obj:`DB`): データベース操作をラップしたオブジェクト。

        """
        self.__db = db
        self.__table_name = Config.TABLE

    def _cursor(self):
        return self.__db.cursor()

    def _get_datetime(self, datetime_str):
        return self.__db.get_datetime(datetime_str)

    def get_all_teams(self):
        """試合スケジュールのある全てのチーム名を返す。

        Returns:
            team_names (list): チーム名のリスト。

        """
        team_names = list()
        cur = self._cursor()
        cur.execute("SELECT home_team FROM " + self.__table_name + ";")
        home_team_rows = cur.fetchall()
        cur.execute("SELECT away_team FROM " + self.__table_name + ";")
        away_team_rows = cur.fetchall()
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
        cur = self._cursor()
        cur.execute("SELECT DISTINCT category FROM " + self.__table_name + ";")
        for row in cur.fetchall():
            categories.append(row["category"])
        return list(filter(lambda a: a != "", categories))

    def get_last_updated(self):
        """テーブルの最終更新日を返す。

        Returns:
            last_updated (:obj:`datetime.datetime'): scheduleテーブルのupdatedカラムで一番最新の値を返す。
        """
        cur = self._cursor()
        cur.execute("SELECT max(updated),updated FROM " + self.__table_name + ";")
        row = cur.fetchone()
        if row["max(updated)"] is None:
            return None
        else:
            # SQLite3にはdatetime型がないが、updatedカラムに時差を考慮した値が
            # 返ってくるようにしている。
            return datetime.strptime(row["max(updated)"], "%Y-%m-%d %H:%M:%S")
