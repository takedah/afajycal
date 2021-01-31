from afajycal.db import DB
from afajycal.errors import DatabaseError, DataError
from afajycal.logs import AppLog
from afajycal.services import ScheduleService


def delete_schedules():
    """試合スケジュールテーブルを全て削除する"""

    db = DB()
    logger = AppLog()
    try:
        schedule_service = ScheduleService(db)
        schedule_service.truncate()
        db.commit()
    except (DatabaseError, DataError) as e:
        db.rollback()
        logger.error(e.args[0])
    finally:
        db.close()


if __name__ == "__main__":
    delete_schedules()
