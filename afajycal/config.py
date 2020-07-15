import os
from datetime import timezone, timedelta


class Config:
    THIS_YEAR = 2020
    JST = timezone(timedelta(hours=+9))
    DATABASE = os.environ.get("AFAJYCAL_DB_URL")
