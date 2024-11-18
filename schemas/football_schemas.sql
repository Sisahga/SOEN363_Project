CREATE TABLE league (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(50),
    api_sports_id INTEGER
);

CREATE TABLE team (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(5),
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    founded INTEGER,
    national_team BOOLEAN,
    FOREIGN KEY(league_id) REFERENCES league(id) ON DELETE CASCADE
);

CREATE TABLE player (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    team_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY(team_id) REFERENCES team(id) ON DELETE CASCADE
);

-- WEAK ENTITY, depends on team
CREATE TABLE team_member (
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    PRIMARY KEY (player_id, team_id),
    FOREIGN KEY(player_id) REFERENCES player(id) ON DELETE CASCADE,
    FOREIGN KEY(team_id) REFERENCES team(id) ON DELETE CASCADE
);

CREATE TABLE team_stats (
    league_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    rank INTEGER,
    games_played INTEGER,
    wins INTEGER,
    losses INTEGER,
    draws INTEGER,
    points INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    goal_difference INTEGER,
    FOREIGN KEY(league_id) REFERENCES league(id),
    FOREIGN KEY(team_id) REFERENCES team(id)
)