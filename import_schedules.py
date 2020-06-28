from afajycal.config import Config
from afajycal.db import DB
from afajycal.models import ScheduleFactory, ScheduleService
from afajycal.scraper import DownloadedHTML, ScrapedHTMLData, DownloadedExcel, ScrapedExcelData


def import_schedules():
    """データベースに試合スケジュールを格納
    """

    # Webサイトからデータを抽出する処理
    try:
        downloaded_html = DownloadedHTML('http://afa11.com/asahijy/reiwa2/nittei2020.html')
        scraped_data = ScrapedHTMLData(downloaded_html)
    except HTMLDownloadError:
        downloaded_excel = DownloadedExcel('http://afa11.com/asahijy/reiwa2/nittei2020.xlsx')
        scraped_data = ScrapedExcelData(downloaded_excel)

    schedule_factory = ScheduleFactory()
    for d in scraped_data.schedule_data:
        schedule_factory.create(d)

    # 抽出データをデータベースへ格納する処理
    db = DB(Config.DATABASE)
    schedule_service = ScheduleService(db)
    schedule_service.truncate()
    for schedule in schedule_factory.items:
        schedule_service.create(schedule)
    db.commit()
    db.close()


if __name__ == "__main__":
    import_schedules()
