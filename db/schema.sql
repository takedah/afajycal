DROP TABLE IF EXISTS schedules;
CREATE TABLE schedules(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  serial_number VARCHAR(8) UNIQUE NOT NULL,
  category VARCHAR(8),
  match_number VARCHAR(8),
  match_date DATE,
  kickoff_time DATETIME,
  home_team VARCHAR(32),
  away_team VARCHAR(32),
  studium VARCHAR(32),
  updated_at DATETIME NOT NULL
);
