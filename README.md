# AFA junior youth soccer match calendar

旭川地区サッカー協会第3種事業委員会Webサイトから、試合日程データをダウンロードして検索できるようにするものです。
FlaskとSQLite3を使っています。

## Description

1. 旭川地区サッカー協会第3種事業委員会Webサイトから試合日程の掲載されているページをダウンロードして必要なデータを抽出します。
2. 抽出したデータをSQLite3データベースに格納します。
3. Webフォームでチーム名、カテゴリごとに試合日程を検索できるようになります。

## Requirement

- SQLite3
- requests
- BeautifulSoup4
- flask

## Install

```bash
$ make
$ python
>>> from afajycal.action import MatchScheduleAction
  >>> MatchScheduleAction.create()
>>> quit()
  ```

## Usage

  ```bash
  $ FLASK_APP=afajycal/view.py flask run
  ```

## Lisence

  Copyright (c) 2019 Hiroki Takeda
  [MIT](http://opensource.org/licenses/mit-license.php)
