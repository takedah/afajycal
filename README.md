# AFA junior youth soccer match calendar

This is a web application which can search AFA junior youth soccer match shcedule.
This web application is composed of Flask web application framework.

## Description

1. This system downloads AFA junior youth soccer match schedule data from AFA Web site.
2. downloaded data are imported into the SQLite3 database.
3. You can get match schedule data which is specified by conditions(category, team name) from this database through this system.

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
