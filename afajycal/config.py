from datetime import timedelta, timezone


class Config:
    AFA_URL = "http://afa11.com/asahijy/heisei31/nittei2019.html"
    THIS_YEAR = 2019
    DATABASE = "afajycal/afajycal.db"
    TABLE = "schedules"
    JST = timezone(timedelta(hours=+9), "JST")
