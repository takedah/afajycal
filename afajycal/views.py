from datetime import datetime, timedelta, timezone

from flask import Flask, escape, g, render_template, request

from afajycal.config import Config
from afajycal.db import DB
from afajycal.services import ScheduleService

app = Flask(__name__)
THIS_YEAR = Config.THIS_YEAR


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
    return DB()


def get_db():
    if not hasattr(g, "postgres_db"):
        g.postgres_db = connect_db()
    return g.postgres_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "postgres_db"):
        g.postgres_db.close()


@app.route("/")
def index():
    JST = Config.JST
    date_now = datetime.now(JST)
    schedule_service = ScheduleService(get_db())
    today_schedules = schedule_service.find(match_date=date_now.date())
    all_teams = schedule_service.get_all_teams()
    all_categories = [""] + schedule_service.get_all_categories()
    title = "AFA Junior Youth Calendar"
    return render_template(
        "index.html",
        title=title,
        this_year=THIS_YEAR,
        teams=all_teams,
        categories=all_categories,
        date_now=date_now.date().strftime("%Y-%m-%d %a"),
        schedules=today_schedules,
        results_number=len(today_schedules),
        last_update=schedule_service.get_last_updated().strftime("%Y/%m/%d %H:%M"),
    )


@app.route("/find")
def find():
    team_name = request.args.get("team_name", None)
    category = request.args.get("category", None)
    if team_name == "":
        team_name = None
    else:
        team_name = escape(team_name)
    if category == "":
        category = None
    else:
        category = escape(category)

    schedule_service = ScheduleService(get_db())
    found_schedules = schedule_service.find(team_name=team_name, category=category)
    all_teams = schedule_service.get_all_teams()
    all_categories = [""] + schedule_service.get_all_categories()
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
        teams=all_teams,
        categories=all_categories,
        team_name=team_name,
        category=category,
        schedules=found_schedules,
        results_number=len(found_schedules),
        last_update=schedule_service.get_last_updated().strftime("%Y/%m/%d %H:%M"),
    )


@app.errorhandler(404)
def not_found(error):
    schedule_service = ScheduleService(get_db())
    all_teams = schedule_service.get_all_teams()
    all_categories = [""] + schedule_service.get_all_categories()
    title = "404 Page Not Found."
    return render_template(
        "404.html", title=title, teams=all_teams, categories=all_categories
    )


if __name__ == "__main__":
    app.run(debug=True)
