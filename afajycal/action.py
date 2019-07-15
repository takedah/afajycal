import sqlite3
import re
from datetime import datetime, timedelta, timezone
from afajycal.config import Config
from afajycal.db import DB
from afajycal.scraper import Scraper
from afajycal.models import MatchSchedule


class DatabaseActionError(Exception):
    pass


class MatchScheduleAction:
    """
    旭川地区サッカー協会第3種事業委員会Webサイトから試合スケジュールを取得する。

    """
    @classmethod
    def create(self):
        """
        旭川地区サッカー協会第3種事業委員会Webサイトからダウンロードした
        データを、データベースへ登録する。登録の時、既存のデータベースの
        データは一旦全て削除してから処理を行う。

        Returns
        -------
        process_result : boolean
            データの登録が成功したら、Trueを返す。失敗したら、Falseを返す。

        """
        db = DB(Config.DATABASE)
        cur = db.cursor()
        scraper = Scraper()
        try:
            cur.execute('DELETE FROM match_schedules')
            values = list()
            now_time = datetime.now(timezone(timedelta(hours=+9), 'JST'))
            match_list = scraper.get_schedule_list()
            for row in match_list:
                tmp = list()
                tmp = [
                    row['number'],
                    row['category'],
                    row['match_number'],
                    row['match_date'],
                    row['kickoff_time'],
                    row['home_team'],
                    row['away_team'],
                    row['studium'],
                    now_time]
                values.append(tmp)

            cur.executemany(
                'INSERT OR IGNORE INTO match_schedules ('
                + 'number, category, match_number, match_date, '
                + 'kickoff_time, home_team, away_team, studium, '
                + 'updated) VALUES (?,?,?,?,?,?,?,?,?);',
                values)
            db.commit()
            db.close()
            print('schedules data imported successfully.')
            return True

        except sqlite3.Error:
            db.close()
            raise DatabaseActionError

    @classmethod
    def get_team_names(self):
        """
        全てのチーム名を返す。

        Returns
        -------
        team_names : list
            チーム名のリスト。

        """

        db = DB(Config.DATABASE)
        cur = db.cursor()
        team_names = list()
        try:
            cur.execute("SELECT home_team FROM match_schedules")
            home_team_rows = cur.fetchall()
            cur.execute("SELECT away_team FROM match_schedules")
            away_team_rows = cur.fetchall()
            db.close()
            for row in home_team_rows:
                team_names.append(row['home_team'])

            for row in away_team_rows:
                team_names.append(row['away_team'])

            team_names = list(filter(lambda a: a != "", team_names))
            team_names = sorted(set(team_names), key=team_names.index)
            return team_names

        except sqlite3.Error:
            db.close()
            raise DatabaseActionError

    @classmethod
    def get_number_of_matches(self, team_name, date_time):
        """
        対象チームの試合数を返す。

        Parameters
        ----------
        team_name : str
            対象のチーム名。

        Returns
        -------
        number_of_matches : int
            対象のチームの試合数。
        date_time : datetime
            基準の日時。

        """

        db = DB(Config.DATABASE)
        cur = db.cursor()
        number_of_matches = 0
        try:
            cur.execute(
                "SELECT COUNT(*) FROM match_schedules"
                + " " + "WHERE home_team=? OR away_team=?"
                + " " + "AND kickoff_time > ?",
                (team_name, team_name, date_time))
            row = cur.fetchone()
            db.close()
            number_of_matches = row[0]
            return number_of_matches

        except sqlite3.Error:
            db.close()
            raise DatabaseActionError

    @classmethod
    def get_categories(self):
        """
        全てのカテゴリ名を返す。

        Returns
        -------
        categories : list
            カテゴリ名のリスト。

        """
        db = DB(Config.DATABASE)
        cur = db.cursor()
        categories = list()
        try:
            cur.execute("SELECT DISTINCT category FROM match_schedules")
            rows = cur.fetchall()
            db.close()
            for r in rows:
                categories.append(r['category'])

            # remove empty elements.
            categories = list(filter(lambda a: a != "", categories))

            return categories

        except sqlite3.Error:
            db.close()
            raise DatabaseActionError

    @staticmethod
    def _trim_team_name(team_name):
        """
        データベースに登録されているチーム名が「旭川市立」で始まったり、
        「中学校」、「中」で終わっていないため、チーム名を検索できるよう、
        これらの文字列を削除する。

        Parameters
        ----------
        team_name : str
            元のチーム名。

        Returns
        -------
        trimed_team_name : str
            文字列削除後のチーム名。

        """
        team_name = team_name.strip()
        if re.search(r'^旭川市立', team_name):
            team_name = team_name.replace('旭川市立', '')

        if re.search(r'学校$', team_name):
            team_name = team_name.replace('学校', '')

        if re.search(r'中$', team_name):
            team_name = team_name.replace('中', '')

        trimed_team_name = team_name.strip()
        return trimed_team_name

    @classmethod
    def find(self, team_name, category, date_time):
        """
        基準日時以降の対象のチーム・カテゴリの全ての試合スケジュールを返す。

        Parameters
        ----------
        team_name : str
            対象のチーム名。
        category : str
            対象のカテゴリ名。
        date_time : datetime
            基準の日時。

        Returns
        -------
        results : list of MatchSchedule object
            試合スケジュールデータ。
        number : int
            検索結果の試合数。

        """
        db = DB(Config.DATABASE)
        cur = db.cursor()
        results = list()
        number = 0
        try:
            team_name = self._trim_team_name(team_name)
            if team_name == '' or team_name == '全て':
                team_name = '%'
            else:
                team_name = '%' + team_name + '%'

            if category == '' or category == '全て':
                category = '%'
            else:
                category = '%' + category + '%'

            search_condition = "WHERE" + " " \
                + "(home_team LIKE ? OR away_team LIKE ?)" \
                + " " + "AND category LIKE ?" \
                + " " + "AND kickoff_time > ?"
            search_value = (team_name, team_name, category, date_time)
            cur.execute(
                "SELECT" + " "
                + "id,number,category,match_number,match_date,kickoff_time,"
                + "home_team,away_team,studium,updated" + " "
                + "FROM match_schedules" + " "
                + search_condition + " "
                + "ORDER BY kickoff_time;",
                search_value)
            rows = cur.fetchall()
            cur.execute(
                "SELECT COUNT(*) FROM match_schedules"
                + " " + search_condition + ";",
                search_value)
            row = cur.fetchone()
            db.close()
            number = row[0]
            for r in rows:
                results.append(MatchSchedule(**r))

            return results, number

        except sqlite3.Error:
            db.close()
            raise DatabaseActionError

    @classmethod
    def day_match(self, target_date):
        """
        基準日に行われる試合スケジュールのみ返す。

        Parameters
        ----------
        target_date : date
            基準の日時。

        Returns
        -------
        results : list of MatchSchedule object
            試合スケジュールデータ。
        number : int
            検索結果の試合数。

        """
        db = DB(Config.DATABASE)
        cur = db.cursor()
        results = list()
        number = 0
        try:
            search_condition = "WHERE match_date = ?"
            search_value = (target_date,)
            cur.execute(
                "SELECT" + " "
                + "id,number,category,match_number,match_date,kickoff_time,"
                + "home_team,away_team,studium,updated" + " "
                + "FROM match_schedules" + " "
                + search_condition + " "
                + "ORDER BY kickoff_time;",
                search_value)
            rows = cur.fetchall()
            cur.execute(
                "SELECT COUNT(*) FROM match_schedules"
                + " " + search_condition + ";",
                search_value)
            row = cur.fetchone()
            db.close()
            number = row[0]
            for r in rows:
                results.append(MatchSchedule(**r))

            return results, number

        except sqlite3.Error:
            db.close()
            raise DatabaseActionError

    @classmethod
    def get_last_update(self):
        """
        データベースの最終更新日を返す。

        Returns
        -------
        last_update : str
            最終更新年月日。

        """
        db = DB(Config.DATABASE)
        cur = db.cursor()
        try:
            cur.execute(
                "SELECT max(updated),updated FROM match_schedules;"
            )
            row = cur.fetchone()
            db.close()
            if row[0] is None:
                return ''
            else:
                last_update = MatchSchedule.get_datetime(row[0])
                return datetime.strftime(last_update, '%Y/%m/%d %H:%M JST')

        except sqlite3.Error:
            db.close()
            raise DatabaseActionError
