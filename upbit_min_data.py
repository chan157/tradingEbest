import uuid
import hashlib
from urllib.parse import urlencode
import jwt
import requests
import json

access_key = "vdxtgVaR4UMONeWA20oNmfa0sZNg3dmWHixgXa0b"
secret_key = "tWodVzxfuxl75xZ5K2bxMwORsQnwdlQ1uGgSeU9E"
server_url = "https://api.upbit.com"

payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
}

jwt_token = jwt.encode(payload, secret_key)
authorize_token = 'Bearer {}'.format(jwt_token)
headers = {"Authorization": authorize_token}

res = requests.get(server_url + "/v1/accounts", headers=headers)
account_data = res.json()


url = "https://api.upbit.com/v1/candles/minutes/1"

querystring = {"market":"KRW-BTC","count":"10"}

headers = {"Accept": "application/json"}

response = requests.request("GET", url, headers=headers, params=querystring)

price_data = json.loads(response.text)

for price in price_data:
    print(price)