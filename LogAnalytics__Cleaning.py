# Importing libraries

import glob
import sys, os
import time
import requests
import json
import numpy as np
import pandas as pd
import re
import datetime
pd.set_option('display.max_colwidth',0)
pd.set_option('display.max_columns',None)
from bs4 import BeautifulSoup
pd.options.mode.chained_assignment = None


# Importing all the files from the destination

def all_files():
     
    global file
    
    file = []

    date_range = ['%.2d' % i for i in range(1,40)]
    month_range = ['%.2d' % i for i in range(1,15)]
    path = sys.argv[1] # specify the path as the 1st argument while running this script in command prompt
    for month in month_range:
        for dates in date_range:
            filenames = glob.glob((path + '\\*{}{}.log.gz'.format(month, dates)))
            if filenames == []:
                continue
            elif filenames in file:
                continue
            else:
                file.append(filenames)

def reading_files(file):
    
    columns = ['date', 'time', 's-sitename', 's-computername', 's-ip', 'cs-method', 'cs-uri-stem', 
               'cs-uri-query','s-port','cs-username', 'c-ip', 'cs-version', 'cs(User-Agent)', 'cs(Cookie)', 
               'cs(Referer)', 'cs-host', 'sc-status', 'sc-substatus', 'sc-win32-status', 'sc-bytes', 
               'cs-bytes', 'time-taken']
    
    global df_raw1

    df_raw = pd.DataFrame([]) 
        
    for f in file: 
        for files in f:
            df = pd.read_csv(files, names=columns, encoding = 'cp1256',  sep=r'\s+', low_memory=False)
            df_raw = df_raw.append(df)   

        df_raw = df_raw[~df_raw.date.str.startswith('#')].reset_index()
        df_raw = df_raw.drop(columns = 'index').dropna().drop_duplicates()

        # Creating datetime column from date and time and dropping them afterwards:
        df_raw1['datetime'] = pd.to_datetime(df_raw1['date'] + " " + df_raw1['time']) 
        df_raw1 = df_raw1.drop(columns = ['date', 'time'])   

def creating_sessions():
    
    global df_raw3

    # creating uniqueid for each of the users
    df_raw2  = df_raw1.copy()
    df_raw2['uniqueid'] = df_raw2['c-ip'] + '_' + df_raw2['cs(User-Agent)']

    # creating time_gap of each request made by each user
    df_raw2['time_gap'] = df_raw2.sort_values(['uniqueid', 'datetime']).groupby('uniqueid')['datetime'].diff().fillna(0)

    #finding users with time_gap more than 1 hour
    delta = datetime.timedelta(hours = 0.5)
    users = df_raw2[df_raw2['time_gap'] > delta]
    users_list = users['uniqueid'].tolist()

    # multi users mean that the user had multiple sessions
    # single users mean that the user had single sessions
    df_multi_users = df_raw2[df_raw2['uniqueid'].isin(users_list)]
    df_single_users = df_raw2[~df_raw2['uniqueid'].isin(users_list)]

    # defining session ids for single users
    df_single_users = df_single_users.copy()
    df_single_users['sessionid'] = df_single_users['uniqueid'] + '_0'
    df_single_users['sessioncount'] = 1

    # defining session ids for multi users
    session_count = users.groupby('uniqueid').size().reset_index(name = 'sessioncount')
    users = pd.merge(users, session_count, on = 'uniqueid')

    users['sessioncount'] = users['sessioncount'].astype(int) + 1
    users['sessioncount'] = users['sessioncount'].astype(str)

    for_sessions = users[['uniqueid', 'sessioncount']].drop_duplicates()

    sessionlist = pd.DataFrame([])

    for items in for_sessions.iterrows():
        for k in range(1, int(items[1]['sessioncount'])):
            items[1]['sessionid'] = items[1]['uniqueid'] + "_" + str(k)
            sessionlist = sessionlist.append({'sessionid': items[1]['sessionid']}, ignore_index = True)

    sessions = pd.concat([sessionlist, users], axis = 1)
    sessionids = sessions.drop('sessioncount', axis = 1)
    sessions_c = sessions[['uniqueid', 'sessioncount']].drop_duplicates()

    df_multi_users = pd.merge(sessionids, df_multi_users, on = ['s-sitename', 's-computername', 's-ip', 'cs-method', 'cs-uri-stem',
           'cs-uri-query', 's-port', 'cs-username', 'c-ip', 'cs-version',
           'cs(User-Agent)', 'cs(Cookie)', 'cs(Referer)', 'cs-host', 'sc-status',
           'sc-substatus', 'sc-win32-status', 'sc-bytes', 'cs-bytes', 'time-taken',
           'datetime', 'uniqueid', 'time_gap'], how = 'outer')

    df_multi_users = df_multi_users.sort_values(by = ['uniqueid', 'datetime'])
    df_multi_users = df_multi_users.groupby('uniqueid').ffill()
    p = df_multi_users['uniqueid'] + '_0' 
    df_multi_users['sessionid'] = df_multi_users['sessionid'].fillna( p)

    df_multi_users = pd.merge(df_multi_users, sessions_c, on = 'uniqueid', how = 'outer')

    # Concatenating single and multi users together 
    df_raw3 = pd.concat([df_multi_users, df_single_users])
    
    # creating 'numberofhits' column to count the number of hits made by each session
    df_raw3['numberofhits'] = df_raw3.groupby('sessionid')['c-ip'].transform(np.size)

    # Changing the data type of sessioncount from object to integer
    df_raw3['sessioncount'] = df_raw3['sessioncount'].astype(int)

     
def step1_cleaning():

    global data_clean

    # listing down the keywords which are found only in the user-agent of bot
    antiq_agents = ['HeadlessChrome', 'PhantomJS', 'CasperJS', 'YaBrowser', 'yandex', 'coccocbot', 'coc_coc', 'Yowser', 
                    'Electron', 'chromeframe', 'Camino', 'AppEngine-Google', 'x.x.x']
    lib_agents = ['Apache-HttpClient', 'libwww', 'perl', 'masscan', 'github']
    bot_agents = ['bot', 'crawl', 'Magic', 'BingPreview', 'metauri', 'curl', 'Diagnostics', 'Antivirus', 'spam', 'dataxu', 
                  'parse', 'MagpieRSS', 'EasyBib', 'NING', 'Dispatch', 'Certificate', 'lwp-trivial', 'Twisted', 'PageGetter', 
                  'scrap', 'Iframely', 'muhstik-scan', 'analyze', 'HubSpot', 'Professional', 'AddThis.com', 'FeedBurner',
                  'package', 'monitor', 'expo', 'python', 'ltx71', 'favicon', 'spider', 'prox', 'hit', 'bub', 'law', 'exact', 
                  'admantx', 'httpsearch', 'cloud', 'archive', 'webinject', 'asafaweb.com', 'meltwater', 'ptst', 'qwant', 'ad-',
                  'slurp', 'runscope', 'nodeping', 'mediapartner', 'linkcheck', 'snapshot', 'Saleslift', 'gooblog', 
                  'Go-http-client', 'restsharp', 'POE-Component', 'unirest', 'okhttp', 'Scoop.it', 'dotbot', 'Yeti', 'seo', 
                  'AhrefsBot', 'Indexer', 'duckduckgo', 'sogou', 'Exabot', 'mailto', 'facebookexternal', 'Java/1.8.0', 
                 'Jersey', 'Pcore', 'test', 'wordpress', 'newspaper', 'Callpod', 'WhatsApp', 'fetch', 'SafariViewService', 
                  'Extension', 'Dorado', 'marketinggrader', 'Grammarly', 'Ruby', 'social', 'HttpClient', 'Uzbl', 
                 'process', 'job', 'Drupal']
    bot_keywords = antiq_agents + lib_agents + bot_agents

    # keeping only those user-agents which are in the below format
    data_clean = df_raw3[df_raw3['cs(User-Agent)'].str.contains(r'[\/\+._;]+')]
    
    # cleaning out all the users whose user agent contain any of the bot keywords
    data_clean = data_clean[~data_clean['cs(User-Agent)'].str.contains('|'.join(bot_keywords), case = False)]


# I analyzed and found some other bots on Project Honeybot. 
#They looked very authentic to me and I decided to include them in my analysis. 
#For more information, please visit : https://www.projecthoneypot.org/

def honeybots_scraping():
    
    global bot_df
    
    link = 'https://www.projecthoneypot.org/harvester_useragents.php'
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    html = list(soup.children)[2]
    body = list(html.children)[3]
    div = list(body.children)[5]
    div2 = list(div.children)[5]
    o = list(div2.children)[1]
    i = list(o.children)[3]
    e = list(i.children)[3]
    list1 = []
    for a in e.find_all('a'):
        list1.append(a.string)

    bot_df = pd.DataFrame([])
    for k in list1:
        h = k.replace(' ', '+')
        bot_df = bot_df.append({'User-Agent': h}, ignore_index=True)

honeybots_scraping()

def step2_cleaning():
    
    global data_clean
    
    # creating a list of all the honeybots
    bot_user_agents = bot_df['User-Agent'].tolist()

    # removing them from the cleaned data from step1
    data_clean = data_clean[~data_clean['cs(User-Agent)'].isin(bot_user_agents)]


def step3_cleaning():

    global data_clean

    df_raw4 = data_clean.copy()

    # Users which have asked for robots.txt 
    robots = df_raw4[df_raw4['cs-uri-stem'].str.contains(r'robots', case = False)]['uniqueid'].unique().tolist() 
    df_robots = df_raw4[df_raw4['uniqueid'].isin(robots)]
    users1 = df_robots['uniqueid'].unique().tolist()

    # if a single session was active for more than 3 hours
    first_last_entry = df_raw4.groupby('sessionid').agg(['first', 'last']).stack().reset_index()
    first_last_entry['diff'] = first_last_entry.groupby('sessionid')['datetime'].diff().fillna(0).dt.total_seconds()
    main = first_last_entry[first_last_entry['level_1'] == 'last']
    df_3hoursessions = main[main['diff'] >= 10800]  
    users2 = df_3hoursessions['uniqueid'].unique().tolist()

    # if a single ip has more than 50 user agents with it in one day    
    ip_count = df_raw4.groupby(['c-ip', 'cs(User-Agent)']).head()['c-ip'].value_counts().reset_index()
    bot_ip = ip_count[ip_count['c-ip'] > 50]['index'].tolist() 

    # if the number of hits were more than 100 and total pages opened were less than 5, that is bot who got stuck somewhere
    unique_stems = df_raw4.groupby('sessionid')['cs-uri-stem'].nunique().reset_index(name = 'unique_stems')
    df_stuckbot = pd.merge(unique_stems, df_raw4, on = 'sessionid', how = 'outer')
    df_stuckbot = df_stuckbot[(df_raw_3['numberofhits'] >= 100) & (df_raw_3['unique_stems'] <= 5)]
    users3 = df_stuckbot['uniqueid'].unique().tolist()

    # if the user has used the 'HEAD' method, it has to be a bot
    users4 = df_raw4[df_raw4['cs-method'] == 'HEAD']['uniqueid'].tolist()

    # concatenating all the bot users in one list
    bot_users = list(set(users1 + users2 + users3 + users4))

    # removing them from the already clean data from step2 cleaning
    data_clean = data_clean[~data_clean['uniqueid'].isin(bot_users)]
 


# In this way, we can clean majority of the bots from our IIS log files
