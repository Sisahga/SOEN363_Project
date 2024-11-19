CREATE TABLE league (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(50),
    api_sports_id INTEGER UNIQUE
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
    nationality VARCHAR(70)
);

-- WEAK ENTITY: depends on team & player entities
CREATE TABLE team_member (
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    PRIMARY KEY (player_id, team_id),
    FOREIGN KEY(player_id) REFERENCES player(id) ON DELETE CASCADE,
    FOREIGN KEY(team_id) REFERENCES team(id) ON DELETE CASCADE
);

-- IS-A: team_stats extends team as it uses the same primary key as the team table
CREATE TABLE team_stats (
    team_id INTEGER PRIMARY KEY,
    league_id INTEGER NOT NULL,
    rank INTEGER NOT NULL,
    games_played INTEGER,
    wins INTEGER,
    losses INTEGER,
    draws INTEGER,
    points INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    goal_difference INTEGER,
    FOREIGN KEY(league_id) REFERENCES league(id) ON DELETE CASCADE,
    FOREIGN KEY(team_id) REFERENCES team(id) ON DELETE CASCADE
);

CREATE TABLE player_stats (
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    league_id INTEGER NOT NULL,
    games_played INTEGER NOT NULL,
    goals INTEGER,
    assists INTEGER,
    tackles INTEGER,
    dribble_attempts INTEGER,
    dribble_success INTEGER,
    fouls_committed INTEGER,
    yellow_cards INTEGER,
    red_cards INTEGER,
    market_value INTEGER -- use for hardcode view
);

-- Trigger needed before inserting into team_stats.
-- Cannot have 2 teams with the same rank within the same league.
CREATE OR REPLACE FUNCTION enforce_unique_rank()
RETURNS TRIGGER AS
    $$
    BEGIN
        IF EXISTS(
            SELECT 1
            FROM team_stats
            WHERE rank = NEW.rank
            AND league_id = NEW.league_id
            AND team_id != NEW.team_id
        ) THEN
            RAISE EXCEPTION 'Duplicate ranks are not allowed.';
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

CREATE TRIGGER unique_rank_check
    BEFORE INSERT OR UPDATE
    ON team_stats
    FOR EACH ROW
EXECUTE FUNCTION enforce_unique_rank();

-- Hardcoded views based on user access rights
-- 1. Special access view.
CREATE VIEW special_access_player_stats
AS SELECT
       p.id,
       p.first_name,
       p.last_name,
       ps.team_id,
       ps.league_id,
       ps.games_played,
       ps.goals,
       ps.assists,
       ps.tackles,
       ps.dribble_attempts,
       ps.dribble_success,
       ps.fouls_committed,
       ps.yellow_cards,
       ps.red_cards,
       ps.market_value
FROM player as p
JOIN player_stats as ps
ON p.id = ps.player_id;

-- 2. Limited access view (Restrict them from seeing market value)
CREATE VIEW special_access_player_stats
AS SELECT
       p.id,
       p.first_name,
       p.last_name,
       ps.team_id,
       ps.league_id,
       ps.games_played,
       ps.goals,
       ps.assists,
       ps.tackles,
       ps.dribble_attempts,
       ps.dribble_success,
       ps.fouls_committed,
       ps.yellow_cards,
       ps.red_cards
FROM player as p
JOIN player_stats as ps
ON p.id = ps.player_id;