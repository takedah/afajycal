import psycopg2
from psycopg2.extras import DictCursor


class DatabaseError(Exception):
    pass


class DataError(Exception):
    pass


class DB:
    """PostgreSQLデータベースの操作を行う。

    Attributes:
        conn (:obj:`sqlite3.connect`): PostgreSQL接続クラス。

    """

    def __init__(self, dsn):
        """
        Args:
            db_name (str): PostgreSQLデータベースファイル名。

        """
        try:
            self.__conn = psycopg2.connect(dsn)
            self.__cursor = self.__conn.cursor(cursor_factory=DictCursor)
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            raise DatabaseError(e.args[0])

    def execute(self, sql, parameters=None):
        """cursorオブジェクトのexecuteメソッドのラッパー。

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

    def fetchone(self):
        """cursorオブジェクトのfetchoneメソッドのラッパー。

        Returns:
            results (:obj:`Cursor`): 検索結果のイテレータ

        """
        return self.__cursor.fetchone()

    def fetchall(self):
        """cursorオブジェクトのfetchallメソッドのラッパー。

        Returns:
            results (:obj:`Cursor`): 検索結果のイテレータ

        """
        return self.__cursor.fetchall()

    def commit(self):
        """PostgreSQLデータベースにクエリをコミットする。"""
        self.__conn.commit()
        return True

    def rollback(self):
        """PostgreSQLデータベースのクエリをロールバックする。"""
        self.__conn.rollback()
        return True

    def close(self):
        """PostgreSQLデータベースへの接続を閉じる。"""
        self.__conn.close()
        return True
