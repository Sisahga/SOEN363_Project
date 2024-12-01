import psycopg2
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import SON

load_dotenv()
# PostgreSQL connection parameters
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
pg_params = {
    'dbname': db_name,
    'user': db_user,
    'host': db_host,
    'port': db_port,
}

# MongoDB connection parameters
mongo_uri = 'mongodb+srv://everyone:everyone@macmeecluster.he3iw.mongodb.net/'


def migrate_data():
    # Establish PostgreSQL connection
    pg_conn = psycopg2.connect(**pg_params)
    pg_cursor = pg_conn.cursor()

    mongo_client = MongoClient(mongo_uri)
    mongo_db = mongo_client["footballdb"]

    players_collection = mongo_db["players"]
    teams_collection = mongo_db["teams"]
    team_members_collection = mongo_db["team_members"]
    leagues_collection = mongo_db["leagues"]
    player_stats_collection = mongo_db["player_stats"]

    # Step 1: Fetch data from PostgreSQL
    pg_cursor.execute("SELECT * FROM player")
    players = pg_cursor.fetchall()

    pg_cursor.execute("SELECT * FROM team")
    teams = pg_cursor.fetchall()

    pg_cursor.execute("SELECT * FROM team_member")
    team_members = pg_cursor.fetchall()

    pg_cursor.execute("SELECT * FROM league")
    leagues = pg_cursor.fetchall()

    pg_cursor.execute("SELECT * FROM player_stats")
    player_stats = pg_cursor.fetchall()

    # Step 2: Insert leagues into MongoDB and store their MongoDB ObjectIds
    league_id_map = {}
    for league in leagues:
        league_data = {
            "name": league[1],  # Assuming league[1] is name
            "country": league[2],  # Assuming league[2] is country
            "apiFootballId": league[3],  # Assuming league[3] is api_football_id
            "fbOrgId": league[4],  # Assuming league[4] is fb_org_id
            "fbOrgLeagueCode": league[5]  # Assuming league[5] is fb_org_league_code
        }
        result = leagues_collection.insert_one(league_data)
        league_id_map[league[0]] = result.inserted_id  # Map PostgreSQL leagueId to MongoDB ObjectId

    # Step 3: Insert players into MongoDB and store their MongoDB ObjectIds
    player_id_map = {}
    for player in players:
        player_data = {
            "playerId": player[0],  # Assuming player[0] is playerId in your table
            "firstName": player[1],  # Adjust columns as needed
            "lastName": player[2],
            "position": player[3],
            "nationality": player[4]
        }
        result = players_collection.insert_one(player_data)
        player_id_map[player[0]] = result.inserted_id  # Map PostgreSQL playerId to MongoDB ObjectId

    # Step 4: Insert teams into MongoDB and store their MongoDB ObjectIds
    team_id_map = {}
    for team in teams:
        team_data = {
            "teamId": team[0],  # Assuming team[0] is teamId in your table
            "name": team[1],
            "code": team[2],
            "season": team[3],
            "founded": team[4],
            "nationalTeam": team[5],
            "apiFootballId": team[6],
            "fbOrgId": team[7],
            "clubColors": team[8],
            # Link to the league in MongoDB by storing the ObjectId
            "leagueId": league_id_map.get(team[2])  # Assuming team[2] is the league_id
        }
        result = teams_collection.insert_one(team_data)
        team_id_map[team[0]] = result.inserted_id  # Map PostgreSQL teamId to MongoDB ObjectId

    # Step 5: Insert team_member data into MongoDB with references to ObjectIds
    for tm in team_members:
        # Find corresponding player and team ObjectIds from the maps
        player_object_id = player_id_map.get(tm[0])  # Assuming tm[0] is player_id
        team_object_id = team_id_map.get(tm[1])  # Assuming tm[1] is team_id

        if player_object_id and team_object_id:
            team_member_data = {
                "playerId": player_object_id,
                "teamId": team_object_id,
                "season": tm[2]  # Assuming tm[2] is season
            }
            team_members_collection.insert_one(team_member_data)

    # Step 6: Insert player_stats data into MongoDB with references to ObjectIds
    for ps in player_stats:
        # Find corresponding player and team ObjectIds from the maps
        player_object_id = player_id_map.get(ps[0])  # Assuming ps[0] is player_id
        team_object_id = team_id_map.get(ps[1])  # Assuming ps[1] is team_id
        league_object_id = league_id_map.get(ps[2])  # Assuming ps[2] is league_id

        if player_object_id and team_object_id and league_object_id:
            player_stat_data = {
                "playerId": player_object_id,
                "teamId": team_object_id,
                "leagueId": league_object_id,
                "season": ps[3],  # Assuming ps[3] is season
                "gamesPlayed": ps[4],  # Assuming ps[4] is games_played
                "goals": ps[5],  # Assuming ps[5] is goals
                "assists": ps[6],  # Assuming ps[6] is assists
                "yellowCards": ps[7],  # Assuming ps[7] is yellow_cards
                "redCards": ps[8],  # Assuming ps[8] is red_cards
                "marketValue": ps[9]  # Assuming ps[9] is market_value
            }
            player_stats_collection.insert_one(player_stat_data)

    # Close PostgreSQL connection
    pg_cursor.close()
    pg_conn.close()

    print("Migration complete!")

migrate_data()