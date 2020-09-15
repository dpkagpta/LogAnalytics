# Importing required libraries
import time
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import json


# scraping markets

s = time.time()

header = {'User-Agent' : 'DATASCIENCE_Project'}

market_url = r'https://api.*****.com/api/v2/Detail/Markets?partnerid=1'
markets = pd.DataFrame(columns = ['Market_Id', 'MarketName', 'StateAbbr', 'StateName'])

market_response = requests.get(market_url, headers = header)
markets_json = market_response.json()
market_results = markets_json['Result']

for results in market_results:
    Id = results['Id']
    MarketName = results['Name']
    StateAbbr = results['StateAbbr']
    StateName = results['StateName']
    markets = markets.append({'Market_Id': Id, 'MarketName': MarketName, 'StateAbbr': StateAbbr, 'StateName': StateName },ignore_index = True)
markets_list = markets['Market_Id'].unique().tolist()

print('Scraping done and saved!')




# scraping anothet API 

communities = pd.DataFrame({'Community_Id':[], 'Community_name':[], 'Market_Id':[]})

for market in markets_list:
    comm_url = 'https://api.*******.com/api/v2/Search/Communities?partnerid=1&marketid={}'.format(market)
    try:
        comm_response = requests.get(comm_url)
        comm_text = comm_response.text
        comm_json = json.loads(comm_text)
        comm_communities = comm_json['ResultCounts']['Facets']['Communities']
        for community in comm_communities:
            key1 = community['Key']
            value1 = community['Value']
            communities = communities.append({'Community_Id': key1, 'Community_name':value1,'Market_Id': market}, ignore_index=True)
            del key1
            del value1
        del comm_response
        del comm_text
        del comm_json
        del comm_communities
        
    
    except:
        print(comm_url)


# scraping another API

comm_ids = communities['Community_Id'].astype(int).unique().tolist()

for ids in comm_ids:
    comm_url = 'https://api.*******.com/api/v2/Detail/Community?partnerid=1&commId={}'.format(ids)
    try:
        comm_response = requests.get(comm_url)
        comm_text = comm_response.text
        comm_json = json.loads(comm_text)
        df = pd.DataFrame.from_dict(comm_json, orient = 'index').T
        df.replace({ r'\r' : ' '}, regex=True, inplace=True)

        with open('communities_data.csv', 'a') as comms_data:
            df.to_csv(comms_data, header=False, index=False)

        del comm_response
        del comm_text
        del comm_json
        del df
        
    except:
        print(ids)

print('Communities Scraping Done! Working on homes scraping...')



# scraping homes searches


homes = pd.DataFrame()
non_processed_homes = []

for market in markets_list:    
    try:
        home_url = 'https://api.*******.com/api/v2/Search/Homes?partnerid=1&marketid={}&SortBy=Random&SortSecondBy=None'.format(market)
        res = requests.get(home_url, headers = header)
        res_text = res.text
        res_json = json.loads(res_text)
        bn = res_json['ResultCounts']['HomeCount']
        another_url = 'https://api.newhomesource.com/api/v2/Search/Homes?partnerid=1&marketid={}&SortBy=Random&SortSecondBy=None&pagesize={}'.format(market, bn)
        res = requests.get(another_url, headers = header)
        res_text = res.text
        res_json = json.loads(res_text)
        bn = res_json['Result']
        homes=homes.append(pd.DataFrame(bn))
        del home_url
        del another_url
        del res
        del res_text
        del res_json

    except:
        non_processed_homes.append(market)
        print(market)  

print('Homes scraped!')



# scraping an API

plans = homes[homes['IsSpec'] == 0]['PlanId'].unique().tolist()
non_scraped_plan_details = []


for ids in plans:
    comm_url = 'https://api.*******.com/api/v2/Detail/Home?partnerid=1&planId={}'.format(ids)
    try:
        comm_response = requests.get(comm_url, headers = header)
        comm_text = comm_response.text
        comm_json = json.loads(comm_text)
        df = pd.DataFrame.from_dict(comm_json, orient = 'index').T
        df.replace({ r'\r' : ' '}, regex=True, inplace=True)

        with open('plans_data.csv', 'a') as p:
            df.to_csv(p, header=False, index=False)
        del comm_response
        del comm_text
        del comm_json
        del df
        
    except:
        non_scraped_plan_details.append(ids)
        print(ids)

print('Plans Scraping Done! Working on specs scraping...')



# scraping an API

specs = homes[homes['IsSpec'] == 1]['PlanId'].unique().tolist()

for ids in specs:
    comm_url = 'https://api.*******.com/api/v2/Detail/Home?partnerid=1&specId={}'.format(ids)
    try:
        comm_response = requests.get(comm_url, headers = header)
        comm_text = comm_response.text
        comm_json = json.loads(comm_text)
        df = pd.DataFrame.from_dict(comm_json, orient = 'index').T
        df.replace({ r'\r' : ' '}, regex=True, inplace=True)

        with open('specs_data.csv', 'a') as sp:
            df.to_csv(sp, header=False, index=False)
      
        del comm_response
        del comm_text
        del comm_json
        del df
        
    except:
        print(ids)


print(time.time() - s)
print('Done!')

