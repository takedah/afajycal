from datetime import datetime
from flask import Flask, render_template, escape, request, g
from afajycal.config import Config
from afajycal.db import DB
from afajycal.calendar import Calendar
from afajycal.schedule_finder import ScheduleFinder
from afajycal.schedule_service import ScheduleService


app = Flask(__name__)
THIS_YEAR = Config.THIS_YEAR
JST = Config.JST


@app.after_request
def add_security_headers(response):
    response.headers.add(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self' stackpath.bootstrapcdn.com; \
                    script-src 'self' code.jquery.com cdnjs.cloudflare.com \
                    stackpath.bootstrapcdn.com;",
    )
    response.headers.add("X-Content-Type-Options", "nosniff")
    response.headers.add("X-Frame-Options", "DENY")
    response.headers.add("X-XSS-Protection", "1;mode=block")
    return response


def connect_db():
    return DB(Config.DATABASE)


def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def all_teams():
    schedule_service = ScheduleService(get_db())
    all_teams = schedule_service.get_all_teams()
    return all_teams


def all_categories():
    schedule_service = ScheduleService(get_db())
    all_categories = schedule_service.get_all_categories()
    return ["全てのカテゴリ"] + all_categories


def last_update():
    schedule_service = ScheduleService(get_db())
    last_update = schedule_service.get_last_updated()

    return last_update.strftime("%Y/%m/%d %H:%M JST")


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route("/")
def index():
    date_now = datetime.now(JST).date()
    schedule_finder = ScheduleFinder(get_db())
    schedule_finder.find({"match_date": date_now})
    calendar = Calendar(schedule_finder)
    title = "AFA Junior Youth Calendar"
    return render_template(
        "index.html",
        title=title,
        this_year=THIS_YEAR,
        teams=all_teams(),
        categories=all_categories(),
        date_now=date_now.strftime("%Y-%m-%d %a"),
        calendar=calendar,
        results_number=len(calendar.schedules),
        last_update=last_update(),
    )


@app.route("/find")
def find():
    team_name = request.args.get("team_name", None)
    category = request.args.get("category", None)
    if team_name == "" or team_name is None:
        team_name = None
    else:
        team_name = escape(team_name)
    if category == "全てのカテゴリ" or category == "" or category is None:
        category = None
    else:
        category = escape(category)
    schedule_finder = ScheduleFinder(get_db()).find(
        {"team_name": team_name, "category": category}
    )
    calendar = Calendar(schedule_finder)
    if team_name is None:
        team_name = "全チーム"
    if category is None:
        category = "全カテゴリ"
    title = (
        '"' + "チーム: " + team_name + " " + "カテゴリ: " + category + '"' + " " + "の試合検索結果"
    )
    return render_template(
        "find.html",
        title=title,
        this_year=THIS_YEAR,
        teams=all_teams(),
        categories=all_categories(),
        team_name=team_name,
        category=category,
        calendar=calendar,
        results_number=len(calendar.schedules),
        last_update=last_update(),
    )


@app.errorhandler(404)
def not_found(error):
    schedule_finder = ScheduleFinder(get_db())
    title = "404 Page Not Found."
    return render_template(
        "404.html", title=title, teams=all_teams(), categories=all_categories()
    )


if __name__ == "__main__":
    app.run(debug=True)
