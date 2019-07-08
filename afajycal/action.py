import sqlite3
import re
from datetime import datetime, timedelta, timezone
from afajycal.config import Config
from afajycal.db import DB
from afajycal.scraper import Scraper
from afajycal.models import MatchSchedule


class MatchScheduleAction:
    """
    junior youth soccer match schedule in Asahikawa.
    """
    @classmethod
    def create(self):
        """
        import matches list into shchedule database.

        Returns
        -------
        boolean
            If schedules data import is successfull, return true.
            otherwise return false.
        """
        db = DB(Config.DATABASE)
        cur = db.cursor()
        scraper = Scraper()
        try:
            # clear current table.
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
                    row['kickoff_time'],
                    row['home_team'],
                    row['away_team'],
                    row['studium'],
                    now_time]
                values.append(tmp)

            cur.executemany(
                'INSERT OR IGNORE INTO match_schedules ('
                + 'number, category, match_number, '
                + 'kickoff_time, home_team, away_team, studium, '
                + 'updated) VALUES (?,?,?,?,?,?,?,?);',
                values)
            db.commit()
            db.close()
            print('schedules data imported successfully.')
            return True

        except sqlite3.Error as e:
            db.close()
            print('database error: ', e)
            return False

    @classmethod
    def get_team_names(self):
        """
        get all team names.

        Returns
        -------
        team_names : list
            a list includes team name.
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

            # remove empty elements.
            team_names = list(filter(lambda a: a != "", team_names))
            # get unique team names.
            team_names = sorted(set(team_names), key=team_names.index)
            return team_names

        except sqlite3.Error as e:
            db.close()
            print('database error: ', e)
            return team_names

    @classmethod
    def get_number_of_matches(self, team_name):
        """
        get number of matches for target team.

        Parameters
        ----------
        team_name : str
            target team name

        Returns
        -------
        number_of_matches : int
            number of matches for target team.
        """

        db = DB(Config.DATABASE)
        cur = db.cursor()
        number_of_matches = 0
        try:
            cur.execute(
                "SELECT COUNT(*) FROM match_schedules "
                + "WHERE home_team=? OR away_team=?",
                (team_name, team_name))
            row = cur.fetchone()
            db.close()
            number_of_matches = row[0]
            return number_of_matches

        except sqlite3.Error as e:
            db.close()
            print('database error: ', e)
            return False

    @classmethod
    def get_categories(self):
        """
        get all category of AFA junior youth soccer match.

        Returns
        -------
        categories : list
            a category list.
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

        except sqlite3.Error as e:
            db.close()
            print('database error: ', e)
            return categories

    @staticmethod
    def _trim_team_name(team_name):
        """
        If parameter string starts "旭川市立" or parameter string
        ends "中学校" or "中", remove these string for adjusting
        team name to saved team names in DB.

        Parameters
        ----------
        team_name : str
            source team name.

        Returns
        -------
        trimed_team_name : str
            trimed team name.
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
    def find_all(self, team_name, category):
        """
        find targeted team's match schedule.

        Parameters
        ----------
        team_name : str
            target team name.
        category : str
            target match division.

        Returns
        -------
        results : list of MatchSchedule object
            list of tuples which selected from schedule table.

        number : int
            number of list
        """
        db = DB(Config.DATABASE)
        cur = db.cursor()
        results = list()
        number = 0
        try:
            team_name = self._trim_team_name(team_name)
            # If team name is none or "all", select all team.
            if team_name == '' or team_name == 'All':
                team_name = '%'
            else:
                team_name = '%' + team_name + '%'

            # If category is none or "all", select all category.
            if category == '' or category == 'All':
                category = '%'
            else:
                category = '%' + category + '%'

            search_condition = "WHERE" + " " \
                + "(home_team LIKE ? OR away_team LIKE ?)" + " " \
                + "AND category LIKE ?"
            cur.execute(
                "SELECT" + " "
                + "id,number,category,match_number,kickoff_time,"
                + "home_team,away_team,studium,updated" + " "
                + "FROM match_schedules" + " "
                + search_condition + " "
                + "ORDER BY kickoff_time;",
                (team_name, team_name, category))
            rows = cur.fetchall()
            cur.execute(
                "SELECT COUNT(*) FROM match_schedules"
                + " " + search_condition + ";",
                (team_name, team_name, category))
            row = cur.fetchone()
            db.close()
            number = row[0]
            for r in rows:
                results.append(MatchSchedule(**r))

            return results, number

        except sqlite3.Error as e:
            db.close()
            print('database error: ', e)
            return results

    @classmethod
    def find_latest(self, team_name, category, date_time):
        """
        find targeted team's latest match schedule after the targeted date.

        Parameters
        ----------
        team_name : str
            target team name.
        category : str
            target match division.
        date_time : datetime
            base datetime.

        Returns
        -------
        results : MatchSchedule object
            schedule.
        """
        db = DB(Config.DATABASE)
        cur = db.cursor()
        try:
            team_name = self._trim_team_name(team_name)
            # If team name is none or "all", select all team.
            if team_name == '' or team_name == 'All':
                team_name = '%'
            else:
                team_name = '%' + team_name + '%'

            # If category is none or "all", select all category.
            if category == '' or category == 'All':
                category = '%'
            else:
                category = '%' + category + '%'

            cur.execute(
                "SELECT" + " "
                + "id,number,category,match_number,kickoff_time,"
                + "home_team,away_team,studium,updated" + " "
                + "FROM match_schedules" + " "
                + "WHERE (home_team LIKE ? OR away_team LIKE ?)" + " "
                + "AND category LIKE ?"
                + "AND kickoff_time > ? "
                + "ORDER BY kickoff_time "
                + "LIMIT 1;",
                (team_name, team_name, category, date_time))
            row = cur.fetchone()
            db.close()
            if row is None:
                results = None
            else:
                results = MatchSchedule(**row)

            return results

        except sqlite3.Error as e:
            db.close()
            print('database error: ', e)
            return None

    @classmethod
    def get_last_update(self):
        """
        get last update time of 'match_schedules' table.

        Returns
        -------
        last_update : str
          value of newest 'update' column.

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

        except sqlite3.Error as e:
            db.close()
            print('database error: ', e)
            return None
