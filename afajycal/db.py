import sqlite3
from datetime import datetime


class DB:
    """SQLite3の操作で使うメソッドをラップするためのクラス。
    """

    def __init__(self, db_name):
        """
        Args:
            db_name (str): 接続するSQLite3データベース名。

        """

        self.__conn = sqlite3.connect(db_name)
        self.__conn.row_factory = self._dict_factory

    def cursor(self):
        """
        Returns:
            cursor (:obj:`sqlite3.Cursor`): カーソルオブジェクト。

        """

        return self.__conn.cursor()

    def commit(self):
        """
        Returns:
            none: トランザクションをコミットする。

        """
        return self.__conn.commit()

    def close(self):
        """
        Returns:
            none: SQLite3データベースとの接続を閉じる。

        """

        return self.__conn.close()

    @staticmethod
    def get_datetime(datetime_str):
        """SQLite3が返す文字列の日時をdatetime.datetimeオブジェクトに変換する。

        Args:
            datetime_str (str): SQLite3が返す文字列の日時。

        Returns:
            datetime_object (:obj:`datetime.datetime`): datetimeオブジェクト。

        """
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S%z")

    @staticmethod
    def get_date(date_str):
        """SQLite3が返す文字列の日をdatetime.dateオブジェクトに変換する。

        Args:
            date_str (str): SQLite3が返す文字列の日。

        Returns:
            date_object (:obj:`datetime.date`): dateオブジェクト。

        """
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    @staticmethod
    def _dict_factory(cursor, row):
        """SQLite3の検索結果を辞書へ変換する。

        Args:
            cursor (:obj:`sqlite3.Cursor`): Cursorオブジェクト。
            row (list): 値のリスト。

        Returns:
            d (dict): カラム名をキーとして結果を値に格納した辞書。

        """

        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
