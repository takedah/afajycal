import logging
from datetime import datetime


class Log:
    @staticmethod
    def logging_time():
        """ログに記録したい年月日表記で現在時刻を返す

        Returns:
            logging_time (str): 年月日表記文字列

        """

        return datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S")


class DBLog(Log):
    """データベースのエラーログ用"""

    def __init__(self):
        logger = logging.getLogger("DBLog")
        file_handler = logging.FileHandler("logs/db_log.txt")
        for h in logger.handlers:
            logger.removeHandler(h)
        self.__logger = logger
        self.__logger.addHandler(file_handler)

    def _log(self, level, msg):
        """logging.logger.logをラップしただけ

        Args:
            level (int): ログレベル
            msg (str): メッセージ

        """

        return self.__logger.log(level, msg)

    def error_log(self, msg):
        """エラーログ

        Args:
            msg (str): エラーメッセージ

        Returns:
            bool: ログに成功したら真を返す

        """

        log_msg = self.logging_time() + "," + '"' + msg + '"'

        self._log(30, log_msg)
        return True
