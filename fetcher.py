import json
import os

from dotenv import load_dotenv
import requests
import psycopg2

load_dotenv()
x_auth_token = os.getenv('X_AUTH_TOKEN')
x_apisports_key = os.getenv('X_APISPORTS_KEY')
football_data_org_headers = {
    "X-Auth-Token": x_auth_token
}
api_football_headers = {
    "x-apisports-key": x_apisports_key,
}
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_params = {
    'dbname': db_name,
    'user': db_user,
    'host': db_host,
    'port': db_port,
}


# Fetches leagues and populates the league table
# Param 1: year, this is essential for optimizing fetch in API_Football
def fetch_and_store_leagues(year):
    url = f"https://v3.football.api-sports.io/leagues?season={year}"
    response = requests.get(url, headers=api_football_headers)
    leagues = response.json().get("response")

    conn = psycopg2.connect(**db_params)
    print("DB connection successful.")
    cur = conn.cursor()

    for league in leagues:
        print(json.dumps(league, indent=4))
        api_football_id = league["league"]["id"]
        league_name = league["league"]["name"]
        league_country = league["country"]["name"]

        cur.execute("""
        INSERT INTO league (name, country, api_football_id)
        VALUES (%s, %s, %s)
        """, (
            league_name, league_country, api_football_id
        ))
    conn.commit()
    print("Successfully fetched leagues.")
    cur.close()
    conn.close()


# Fetches teams within a league for a specific season.
# Param 1: year - season of the league
# Param 2: api_football_id - to communicate with URL
# Param 3: internal_league_id - to store in team table
# Param 4: cur - cursor for executing queries
def fetch_and_store_teams(year, api_football_league_id, internal_league_id, cur):
    url = f"https://v3.football.api-sports.io/teams?league={api_football_league_id}&season={year}"
    response = requests.get(url, headers=api_football_headers)
    teams = response.json().get("response")

    for team in teams:
        name = team["team"]["name"]
        code = team["team"]["code"]
        founded = team["team"]["founded"]
        national = team["team"]["national"]
        api_football_id = team["team"]["id"]

        cur.execute("""
        INSERT INTO team (name, code, league_id, season, founded, national_team)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            name, code, internal_league_id, year, founded, national
        ))


# Gets all leagues and stores all teams from that league for a specific season
# Communicates with 'fetch_and_store_teams'
def store_teams():
    conn = psycopg2.connect(**db_params)
    print("DB connection successful.")
    cur = conn.cursor()

    cur.execute("SELECT id, api_football_id FROM league")
    rows = cur.fetchall()
    for row in rows:
        fetch_and_store_teams(2022, row[1], row[0], cur)
        print(f"Stored teams from league {row[1]}.")

    conn.commit()
    print("Successfully stored teams.")
    cur.close()
    conn.close()

# fetch_and_store_leagues(2022)


#Fetch Players
# Param 1: api_football_team_id - ID of the team in the API
# Param 2: internal_team_id - ID of the team in the database
# Param 3: season - the season for fetching player data
# Param 4: cur - cursor for executing queries

def fetch_and_store_players(api_football_team_id, internal_team_id, season, cur):
    url = f"https://v3.football.api-sports.io/players?team={api_football_team_id}&season={season}"
    response = requests.get(url, headers=api_football_headers)
    players = response.json().get("response")

    for player_info in players:
        player = player_info["player"]
        player_id = player["id"]
        name = player["name"]
        birth_date = player["birth"]["date"]
        nationality = player["nationality"]
        position = player_info["statistics"][0]["games"]["position"]

        # Insert into the player table
        cur.execute("""
        INSERT INTO player (id, name, birth_date, nationality, position)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """, (
            player_id, name, birth_date, nationality, position
        ))

        # Insert into the team_member table
        cur.execute("""
        INSERT INTO team_member (team_id, player_id, season)
        VALUES (%s, %s, %s)
        """, (
            internal_team_id, player_id, season
        ))
        
# Fetches player stats and populates the player_stats table
# Param 1: api_football_team_id - ID of the team in the API
# Param 2: season - the season for fetching stats
# Param 3: cur - cursor for executing queries

def fetch_and_store_player_stats(api_football_team_id, season, cur):
    url = f"https://v3.football.api-sports.io/players?team={api_football_team_id}&season={season}"
    response = requests.get(url, headers=api_football_headers)
    players = response.json().get("response")

    for player_info in players:
        player_id = player_info["player"]["id"]
        stats = player_info["statistics"][0]  # Assuming the first entry is the main stats

        appearances = stats["games"]["appearences"]
        goals = stats["goals"]["total"]
        assists = stats["goals"]["assists"]
        yellow_cards = stats["cards"]["yellow"]
        red_cards = stats["cards"]["red"]

        # Insert into the player_stats table
        cur.execute("""
        INSERT INTO player_stats (player_id, season, appearances, goals, assists, yellow_cards, red_cards)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            player_id, season, appearances, goals, assists, yellow_cards, red_cards
        ))
# Fetches all players and stats for teams in the database
# Communicates with 'fetch_and_store_players' and 'fetch_and_store_player_stats'
def store_players_and_stats():
    conn = psycopg2.connect(**db_params)
    print("DB connection successful.")
    cur = conn.cursor()

    cur.execute("SELECT id, api_football_id FROM team")
    rows = cur.fetchall()
    for row in rows:
        team_id, api_team_id = row
        season = 2022  # Set the season to fetch data
        fetch_and_store_players(api_team_id, team_id, season, cur)
        fetch_and_store_player_stats(api_team_id, season, cur)
        print(f"Stored players and stats for team {api_team_id}.")

    conn.commit()
    print("Successfully stored players and player stats.")
    cur.close()
    conn.close()
    
store_teams()
