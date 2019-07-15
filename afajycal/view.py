import urllib.parse
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, escape, request
from afajycal.config import Config
from afajycal.action import MatchScheduleAction


web = Flask(__name__)
this_year = str(Config.THIS_YEAR)


def team_names_and_match_number():
    tmp = list()
    for team_name in MatchScheduleAction.get_team_names():
        tmp.append([
            urllib.parse.quote(team_name),
            team_name,
            MatchScheduleAction.get_number_of_matches(team_name)
            ])

    return tmp


def categories():
    categories = MatchScheduleAction.get_categories()
    categories.insert(0, "全て")
    tmp = list()
    for category in categories:
        tmp.append([
            urllib.parse.quote(category),
            category
            ])

    return tmp


@web.after_request
def add_security_headers(response):
    response.headers.add(
        'Content-Security-Policy',
        "default-src 'self'; style-src 'self' stackpath.bootstrapcdn.com; \
                    script-src 'self' code.jquery.com cdnjs.cloudflare.com \
                    stackpath.bootstrapcdn.com;")
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-Frame-Options', 'DENY')
    response.headers.add('X-XSS-Protection', '1;mode=block')
    return response


@web.route('/')
def index():
    last_update = MatchScheduleAction.get_last_update()
    title = 'AFA junior youth match schedules'
    return render_template(
        'index.html', title=title, this_year=this_year,
        team_names_and_match_number=team_names_and_match_number(),
        categories=categories(), last_update=last_update)


@web.route('/find_all')
def find_all():
    category = escape(request.args.get('category'))
    if category == '' or category == 'カテゴリを選択':
        category = '全て'

    team_name = escape(request.args.get('team_name'))
    if team_name == '':
        team_name = '全て'

    JST = timezone(timedelta(hours=+9), 'JST')
    time_now = datetime.now(JST)
    res = MatchScheduleAction.find_all(team_name, category)
    schedule = res[0]
    results_number = res[1]
    next_game = MatchScheduleAction.find_latest(team_name, category, time_now)
    last_update = MatchScheduleAction.get_last_update()
    title = 'Search results of ' + '"' + team_name + \
        '"' + ' "' + category + '"' + ' match schedules'
    return render_template(
        'find_all.html', title=title, this_year=this_year,
        team_name=team_name, category=category,
        team_names_and_match_number=team_names_and_match_number(),
        categories=categories(), schedule=schedule,
        results_number=results_number, next_game=next_game,
        last_update=last_update)


if __name__ == '__main__':
    web.run(debug=True)
