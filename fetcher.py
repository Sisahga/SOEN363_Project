import json
import os

from dotenv import load_dotenv
import requests

load_dotenv()
x_auth_token = os.getenv('X_AUTH_TOKEN')
football_data_org_headers = {
    "X-Auth-Token": x_auth_token
}

url = "https://api.football-data.org/v4/competitions/DED/standings"
response = requests.get(url , headers=football_data_org_headers)
print(json.dumps(response.json(), indent=4))