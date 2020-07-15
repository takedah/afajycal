from afajycal.config import Config
from afajycal.db import DB, DatabaseError, DataError
from afajycal.models import ScheduleFactory, ScheduleService
from afajycal.scraper import (
    DownloadedHTML,
    ScrapedHTMLData,
)


def import_schedules():
    """データベースに試合スケジュールを格納
    """

    # Webサイトからデータを抽出する処理
    downloaded_html = DownloadedHTML("http://afa11.com/asahijy/reiwa2/nittei2020.html")
    scraped_data = ScrapedHTMLData(downloaded_html)
    schedule_factory = ScheduleFactory()
    for d in scraped_data.schedule_data:
        schedule_factory.create(d)

    # 抽出データをデータベースへ格納する処理
    db = DB(Config.DATABASE)
    try:
        schedule_service = ScheduleService(db)
        for schedule in schedule_factory.items:
            schedule_service.create(schedule)
        db.commit()
    except (DatabaseError, DataError) as e:
        db.rollback()
        print(e.args[0])
    finally:
        db.close()


if __name__ == "__main__":
    import_schedules()
