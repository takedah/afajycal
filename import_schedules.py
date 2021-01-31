from afajycal.db import DB
from afajycal.errors import DatabaseError, DataError
from afajycal.logs import AppLog
from afajycal.models import ScheduleFactory
from afajycal.services import ScheduleService
from afajycal.scraper import DownloadedHTML, ScrapedHTMLData


def import_schedules():
    """データベースに試合スケジュールを格納"""

    # Webサイトからデータを抽出する処理
    downloaded_html = DownloadedHTML("http://afa11.com/asahijy/reiwa2/nittei2020.html")
    scraped_data = ScrapedHTMLData(downloaded_html)
    schedule_factory = ScheduleFactory()
    for row in scraped_data.schedule_data:
        schedule_factory.create(**row)

    # 抽出データをデータベースへ格納する処理
    db = DB()
    logger = AppLog()
    try:
        schedule_service = ScheduleService(db)
        for schedule in schedule_factory.items:
            schedule_service.create(schedule)
        db.commit()
    except (DatabaseError, DataError) as e:
        db.rollback()
        logger.error(e.args[0])
    finally:
        db.close()


if __name__ == "__main__":
    import_schedules()
