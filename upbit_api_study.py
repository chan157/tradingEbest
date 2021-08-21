import os
import jwt  # pip install pyjwt 로 설치해야함
import uuid
import hashlib
from urllib.parse import urlencode

import requests

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

print(res.json())



import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import requests


query = {
    'market': 'KRW-ETH',
}
query_string = urlencode(query).encode()

m = hashlib.sha512()
m.update(query_string)
query_hash = m.hexdigest()

payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
    'query_hash': query_hash,
    'query_hash_alg': 'SHA512',
}

jwt_token = jwt.encode(payload, secret_key)
authorize_token = 'Bearer {}'.format(jwt_token)
headers = {"Authorization": authorize_token}

res = requests.get(server_url + "/v1/orders/chance", params=query, headers=headers)

print(res.json())




url = "https://api.upbit.com/v1/market/all"

querystring = {"isDetails":"false"} # 유의종목 필드 출력여부

headers = {"Accept": "application/json"}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)




url = "https://api.upbit.com/v1/candles/minutes/1"

querystring = {"market":"KRW-BTC","to":"","count":"200"}

headers = {"Accept": "application/json"}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)

result = json.loads(response.text)

print(result)



import requests

url = "https://api.upbit.com/v1/orderbook"

querystring = {"markets":"KRW-BTC"}

headers = {"Accept": "application/json"}

response = requests.request("GET", url, headers=headers, params=querystring)

data = json.loads(response.text)
print(data)
