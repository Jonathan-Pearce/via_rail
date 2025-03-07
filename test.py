import sys
#import numpy
import pandas as pd
import urllib.request, json



#with urllib.request.urlopen("https://tsimobile.viarail.ca/data/allData.json") as url:
    #data = json.load(url)
    #print(data)

df = pd.read_json("https://tsimobile.viarail.ca/data/allData.json")
print(df)

print(df['692'])

print(df.loc['from'])

times = df.loc['times']

print(times)