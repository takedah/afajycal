import os
from datetime import timedelta, timezone


class Config:
    THIS_YEAR = 2020
    JST = timezone(timedelta(hours=+9), "JST")
    DATABASE_URL = os.environ.get("AFAJYCAL_DB_URL")
