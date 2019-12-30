import csv
from afajycal.config import Config


class SaveCalendar:
    """試合スケジュールデータを永続化するクラス

    取得した旭川地区サッカー協会第3種事業委員会Webサイトの
    試合スケジュールデータをデータベースまたはファイルへ格納する。

    """

    def __init__(self, args: dict):
        """
        Args:
            args["calendar"] (:obj:`Calendar`): Scheduleクラスのオブジェクトを
                要素とするリストを持つオブジェクト。
            args["db"] (:obj:`DB`): データベース操作をラップしたオブジェクト。

        """

        self.__calendar = args["calendar"]
        self.__db = args["db"]
        self.__table_name = Config.TABLE

    def _schedules(self):
        return self.__calendar.schedules

    def _cursor(self):
        return self.__db.cursor()

    def _commit(self):
        return self.__db.commit()

    def to_csv(self, csv_path):
        """CSVへ試合スケジュールデータを保存

        旭川地区サッカー協会第3種事業委員会Webサイトからダウンロードした
        データを、CSVファイルへ出力する。

        Args:
            csv_path (str): 出力するCSVのパス

        Returns:
            bool: データの登録が成功したらTrueを返す。

        """
        with open(csv_path, "w") as f:
            writer = csv.writer(f)
            for schedule in self._schedules():
                writer.writerow(
                    [
                        schedule.number,
                        schedule.category,
                        schedule.match_number,
                        schedule.match_date,
                        schedule.kickoff_time,
                        schedule.home_team,
                        schedule.away_team,
                        schedule.studium,
                    ]
                )
        return True

    def to_db(self):
        """データベースへ試合スケジュールデータを保存

        旭川地区サッカー協会第3種事業委員会Webサイトからダウンロードした
        データを、データベースへ登録する。登録の時、既存のデータベースの
        データは一旦全て削除してから処理を行う。

        Returns:
            bool: データの登録が成功したらTrueを返す。

        """
        cur = self._cursor()
        cur.execute("DELETE FROM " + self.__table_name)
        for schedule in self._schedules():
            cur.execute(
                "INSERT OR IGNORE INTO"
                + " "
                + self.__table_name
                + " "
                + "(number, category, match_number, match_date, kickoff_time, "
                + "home_team, away_team, studium, updated)"
                + " "
                + "VALUES"
                + " "
                + "(?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'));",
                (
                    schedule.number,
                    schedule.category,
                    schedule.match_number,
                    schedule.match_date,
                    schedule.kickoff_time,
                    schedule.home_team,
                    schedule.away_team,
                    schedule.studium,
                ),
            )
        self._commit()
        return True
