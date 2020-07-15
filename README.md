# AFA junior youth soccer match calendar

旭川地区サッカー協会第3種事業委員会Webサイトから、試合日程データをダウンロードして検索できるようにするものです。
FlaskとPostgreSQLを使っています。

## Description

1. 旭川地区サッカー協会第3種事業委員会Webサイトから試合日程の掲載されているページをダウンロードして必要なデータを抽出します。
2. 抽出したデータをPostgreSQLデータベースに格納します。
3. Webフォームでチーム名、カテゴリごとに試合日程を検索できるようになります。

## Requirement

- PostgreSQL
- BeautifulSoup4
- flask
- gunicorn
- numpy
- pandas
- psycopg2
- requests
- xlrd

## Install

```bash
$ export AFAJYCAL_DB_URL=postgresql://{user_name}:{password}@{host_name}/{db_name}
$ psql -f db/schema.sql -U {user_name} -d {db_name} -h {host_name}
$ make
  ```

## Usage

  ```bash
  $ gunicorn run:app
  ```

## Lisence

  Copyright (c) 2020 Hiroki Takeda
  [MIT](http://opensource.org/licenses/mit-license.php)
