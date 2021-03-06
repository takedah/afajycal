DROP TABLE IF EXISTS schedules;
CREATE TABLE schedules(
  id SERIAL PRIMARY KEY NOT NULL,
  serial_number VARCHAR(8) UNIQUE NOT NULL,
  category VARCHAR(8),
  match_number VARCHAR(8),
  match_date DATE,
  kickoff_time TIMESTAMPTZ,
  home_team VARCHAR(32),
  away_team VARCHAR(32),
  studium VARCHAR(32),
  updated_at TIMESTAMPTZ NOT NULL
);
