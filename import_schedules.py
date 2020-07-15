from afajycal.config import Config
from afajycal.db import DB, DatabaseError, DataError
from afajycal.models import ScheduleFactory, ScheduleService
from afajycal.scraper import (
    DownloadedHTML,
    ScrapedHTMLData,
    DownloadedExcel,
    ScrapedExcelData,
    HTMLDownloadError,
)


def import_schedules():
    """データベースに試合スケジュールを格納
    """

    # Webサイトからデータを抽出する処理
    try:
        downloaded_html = DownloadedHTML(
            "http://afa11.com/asahijy/reiwa2/nittei2020.html"
        )
        scraped_data = ScrapedHTMLData(downloaded_html)
        # downloaded_excel = DownloadedExcel('http://afa11.com/asahijy/reiwa2/nittei2020.xlsx')
        # scraped_data = ScrapedExcelData(downloaded_excel)
    except HTMLDownloadError as e:
        print("ダウンロードに失敗しました。")
        print(e.args[0])

    schedule_factory = ScheduleFactory()
    for d in scraped_data.schedule_data:
        schedule_factory.create(d)

    # 抽出データをデータベースへ格納する処理
    try:
        db = DB(Config.DATABASE)
    except DatabaseError as e:
        print("データベースに接続できませんでした。")
        print(e.args[0])

    schedule_service = ScheduleService(db)
    schedule_service.truncate()
    try:
        for schedule in schedule_factory.items:
            schedule_service.create(schedule)
        db.commit()
    except DataError as e:
        db.rollback()
        print("データ保存に失敗しました。")
        print(e.args[0])
    finally:
        db.close()


if __name__ == "__main__":
    import_schedules()
