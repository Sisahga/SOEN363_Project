import json

import requests

football_data_org_headers = {
    "X-Auth-Token": "7d4fb926a6f841c08db0952194aa0caf"
}

url = "https://api.football-data.org/v4/competitions/DED/standings"
response = requests.get(url , headers=football_data_org_headers)
print(json.dumps(response.json(), indent=4))