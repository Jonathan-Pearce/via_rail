import requests
from datetime import datetime

date = datetime.now().strftime('%Y%m%d')
myFileName = f'raw_data/Via_data_{date}.json'

data_json = requests.get('https://tsimobile.viarail.ca/data/allData.json') 
data = data_json.content
with open(myFileName, 'wb') as f:
    f.write(data)