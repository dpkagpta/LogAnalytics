# Importing libraries

import numpy as np
import pandas as pd
import datetime
from datetime import timedelta

pd.set_option('display.max_colwidth',0)
pd.set_option('display.max_columns',None)
pd.options.mode.chained_assignment = None


file = ['.....1-u_ex181020.log.gz']


def reading_files(file):
    
    columns = ['date', 'time', 's-sitename', 's-computername', 's-ip', 'cs-method', 'cs-uri-stem', 
               'cs-uri-query','s-port','cs-username', 'c-ip', 'cs-version', 'cs(User-Agent)', 'cs(Cookie)', 
               'cs(Referer)', 'cs-host', 'sc-status', 'sc-substatus', 'sc-win32-status', 'sc-bytes', 
               'cs-bytes', 'time-taken']
    
    global df_raw1

    df_raw = pd.DataFrame([]) 
        
    for f in file:
        df = pd.read_csv(f, names=columns, encoding = 'cp1256',  sep=r'\s+', low_memory=False)
        df_raw = df_raw.append(df)   

    df_raw = df_raw[~df_raw.date.str.startswith('#')].reset_index()
    df_raw = df_raw.drop(columns = 'index').dropna().drop_duplicates()

    # Creating datetime column from date and time and dropping them afterwards:
    df_raw1['datetime'] = pd.to_datetime(df_raw1['date'] + " " + df_raw1['time']) 
    df_raw1 = df_raw1.drop(columns = ['date', 'time'])  


def creating_sessions():
    
    global df_with_sessions

    # creating uniqueid for each of the users
    df_raw2  = df_raw1.copy()
    df_raw2['uniqueid'] = df_raw2['c-ip'] + '_' + df_raw2['cs(User-Agent)']

    # creating time_gap of each request made by each user
    df_raw2['time_gap'] = df_raw2.sort_values(['uniqueid', 'datetime']).groupby('uniqueid')['datetime'].diff().fillna(0)

    #finding users with time_gap more than half hour
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
    df_with_sessions = pd.concat([df_multi_users, df_single_users])
    
