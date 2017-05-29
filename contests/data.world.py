"""
This script publishes all *summaries* on data.world.

"""

import os
import requests
import json

dir = 'summaries'
username = 'stsievert'
dataset = 'caption-contest-data'
base_url = ('https://raw.githubusercontent.com/nextml/caption-contest-data/'
            'master/contests/summaries/')


files = [{'name': filename, 'source': {'url': base_url + filename}}
         for filename in os.listdir(dir)
         if filename[0] not in {'_', '.'} and not os.path.isdir(dir + filename)]

token = os.environ.get('DATA_WORLD_TOKEN')
url = f'https://api.data.world/v0/datasets/{username}/{dataset}/files'
data = {'files': files}
headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + token}
data = json.dumps(data)
r = requests.post(url, data=data, headers=headers)
print(r.json())
