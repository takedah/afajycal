from afajycal.config import Config
from afajycal.db import DB, DatabaseError, DataError
from afajycal.models import ScheduleService


def delete_schedules():
    """試合スケジュールテーブルを全て削除する
    """

    db = DB(Config.DATABASE)
    try:
        schedule_service = ScheduleService(db)
        schedule_service.truncate()
        db.commit()
    except (DatabaseError, DataError) as e:
        db.rollback()
        print(e.args[0])
    finally:
        db.close()


if __name__ == "__main__":
    delete_schedules()
