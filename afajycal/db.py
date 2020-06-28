import sqlite3


class DB:
    """SQLite3データベースの操作を行う。

    Attributes:
        conn (:obj:`sqlite3.connect`): SQLite3接続クラス。

    """

    def __init__(self, db_name):
        """
        Args:
            db_name (str): SQLite3データベースファイル名。

        """
        self.__conn = sqlite3.connect(
            db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        sqlite3.dbapi2.converters["DATETIME"] = sqlite3.dbapi2.converters["TIMESTAMP"]
        sqlite3.dbapi2.converters["DATE"] = sqlite3.dbapi2.converters["DATE"]
        self.__conn.row_factory = self._dict_factory
        self.__cursor = self.__conn.cursor()

    @staticmethod
    def _dict_factory(cursor, row):
        """クエリの結果を辞書で受け取れるようにする。
        """

        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def execute(self, sql, parameters=None):
        """sqlite3.cursorオブジェクトのexecuteメソッドのラッパー。

        Args:
            sql (str): SQL文
            parameters (tuple): SQLにプレースホルダを使用する場合の値を格納したリスト

        """
        if parameters:
            self.__cursor.execute(sql, parameters)
        else:
            self.__cursor.execute(sql)
        return True

    def fetchone(self):
        """sqlite3.cursorオブジェクトのfetchoneメソッドのラッパー。

        Returns:
            results (:obj:`sqlite3.Cursor`): 検索結果のイテレータ

        """
        return self.__cursor.fetchone()

    def fetchall(self):
        """sqlite3.cursorオブジェクトのfetchallメソッドのラッパー。

        Returns:
            results (:obj:`sqlite3.Cursor`): 検索結果のイテレータ

        """
        return self.__cursor.fetchall()

    def commit(self):
        """SQLite3データベースにクエリをコミットする。
        """
        self.__conn.commit()
        return True

    def close(self):
        """SQLite3データベースへの接続を閉じる。
        """
        self.__conn.close()
        return True
