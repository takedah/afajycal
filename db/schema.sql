DROP TABLE IF EXISTS match_schedules;
CREATE TABLE match_schedules(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  number BIGINT UNIQUE NOT NULL,
  category VARCHAR(16),
  match_number VARCHAR(16),
  match_date DATE,
  kickoff_time DATETIME,
  home_team VARCHAR(32),
  away_team VARCHAR(32),
  studium VARCHAR(32),
  updated DATETIME NOT NULL
);
