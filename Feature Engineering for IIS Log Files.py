# Importing libraries



date = input('Enter the date for which you want the analysis (yymmdd): ')
import glob
import os
import time
import pickle
import requests
import numpy as np
import pandas as pd
import re
import configparser
import datetime
from datetime import timedelta
from collections import Counter
from bs4 import BeautifulSoup
pd.options.mode.chained_assignment = None
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Required

config = configparser.ConfigParser()
try:
    config.read('config_file.ini')
except:
    print('Config file not found.')

path_to_pick_files_from = config['DEFAULT']['path_to_pick_files_from']
classifier_path = config['DEFAULT']['classifier_path']
path_to_save_files = config['DEFAULT']['path_to_save_files']


# Global Variables

# classifier
classifier_path = os.path.join(classifier_path , 'trained_classifier_for_bot_detection.pkl')
classifier_dump = open(classifier_path, 'rb')
classifier = pickle.load(classifier_dump)

columns = ['date', 'time', 's-sitename', 's-computername', 's-ip', 'cs-method', 'cs-uri-stem', 
               'cs-uri-query','s-port','cs-username', 'c-ip', 'cs-version', 'cs(User-Agent)', 'cs(Cookie)', 
               'cs(Referer)', 'cs-host', 'sc-status', 'sc-substatus', 'sc-win32-status', 'sc-bytes', 
               'cs-bytes', 'time-taken']

scraper_keys = ['.gov','.com', 'Antivirus', 'BUbiNG', 'Barkrowler', 'Callpod', 'Certificate', 'CloudFlare-AlwaysOnline', 'Diagnostics',
     'Dispatch', 'Dorado', 'Drupal', 'EasyBib', 'Extension', 'FeedBurner', 'Go-http-client', 'Grammarly', 'HttpClient',
      'HubSpot', 'HubSpot+inbound+link+reporting+check', 'Iframely', 'Indexer', 'Java/1.8.0', 'Jersey','Magic', 'MagpieRSS',
      'Mediapartners', 'MeltwaterNews', 'MetaURI', 'NING', 'POE-Component', 'PTST', 'PageGetter', 'Pcore','Professional',
      'Proxy', 'Qwantify', 'SafariViewService', 'Saleslift', 'Scoop.it', 'ScoutJet','SpeedCurve', 'Twisted',
      'Uzbl', 'WhatsApp', 'Yeti', '__CT_JOB_ID__', 'ad-', 'admantx', 'ahrefs', 'analytics', 'analyze', 'antenna', 'archive',
     'bot','brain', 'bub', 'check', 'click', 'cloud', 'coc_coc_browser', 'cognitive', 'corpus', 'crawl', 'datamin', 'dataxu',
     'detection', 'exact', 'expo', 'extract', 'favicon', 'feed', 'fetch', 'getintent', 'gooblog',
     'grapeshot', 'hit', 'httpsearch', 'ichiro', 'intelligence', 'job', 'law', 'linkcheck', 'ltx71', 'mailto',
      'mapping', 'marketinggrader', 'mediapartner', 'meltwater', 'monitor', 'netseer', 'news', 'okhttp', 'package', 'paper',
      'parse', 'process', 'proximic', 'ptst', 'python', 'qwant', 'reader', 'researchscan', 'restsharp', 'riddler',
      'runscope-radar', 'scan', 'scrap', 'screenshot', 'search', 'seeker', 'seo', 'snapshot', 'social', 'spam', 'special_archiver',
      'spider', 'test', 'track', 'traveler', 'trovit', 'ubermetrics', 'um-CC', 'um-FC', 'um-LN', 'walker', 'wordpress', 
    'HeadlessChrome', 'PhantomJS', 'CasperJS', 'YaBrowser', 'coccocbot', 'coc_coc', 'Yowser', 
        'Electron', 'chromeframe', 'Camino', 'x.x.x', 'Apache-HttpClient', 'libwww', 'perl', 'masscan', 'github', 'PycURL',
    'curl', 'Ruby','ThousandEyes']

search_engine_keys = ['Googlebot', 'bingbot', 'adsbot',  'Baiduspider', 'Yandex', 'Sogou', 'AppEngine-Google',
                'BingPreview',  'facebookexternalhit', 'Pinterestbot', 'Pingdom', 'adidxbot', 'Qwantify', 'yahoo-ad-monitoring', 
                'Mediapartners-Google', 'GoogleImageProxy', 'Google+Favicon', 'Googlebot-Image', 'YandexMobileBot', 
                 'HeadlessChrome', 'applebot', 'Twitterbot', 'LinkedInBot', 'slurp', 'YaBrowser', 'DeuSu', 'duckduckgo']
bot_keys = scraper_keys + search_engine_keys

# ======================================================================================================================
costa_rica1 = []
for k in range(96, 112):
    costa_rica1.append('186.5.165.' + str(k))
costa_rica2 = []
for k in range(16, 32):
    costa_rica2.append('190.98.188.' +  str(k))
india1 = ['1.22.119.130']
india2 = ['103.79.115.210']
bhi_corp = []
for k in range(0, 256):
    bhi_corp.append('66.194.87.' + str(k))
bhi_guest = ['72.48.145.164']
bhi_lampass1 = ['12.169.107.66']
bhi_lampass2 = ['104.0.143.242']

our_ips = costa_rica1 + costa_rica2 + india1 + india2 + bhi_corp + bhi_guest + bhi_lampass1 + bhi_lampass2
our_ips = ['192.168.102', '192.168.103', '172.16'] + our_ips 
# =======================================================================================================================
def honeybots_scraping():

    global bot_users
    
    try:
        
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
            
    except:
        bot_df = pd.DataFrame()

    # Source : https://blog.sqreen.io/bad-bot-protection/
    l = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1', 
         'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
         'NESSUS::SOAP Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)', 
         'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; SV1)', 
         'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6 MSIE 7.0',
         'Mozilla/5.0 (compatible; Nmap Scripting Engine; http://nmap.org/book/nse.html)', 
         'Mozilla/5.0 (compatible; botify; http://botify.com)']
    bots = []
    for k in l:
        k = k.replace(' ', '+')
        bots.append(k)

    bot_users = bot_df['User-Agent'].tolist() + bots

honeybots_scraping()

# ======================================================================================================================
referers = ['https://www.google.com', 'http://www.google.com', 'https://www.bing', 'http://www.bing', 
                 'android-app://com', 'https://googleads', 'http://googleads', '-']

# ======================================================================================================================
primary_pages = ['/communityresults/' , '/homeresults/', '/boylresults/', '/custom-homes/', '/manufacturedresults/', 
                 '/manufactured-homes/'] 
quick_links = ['/startfresh/', '/luxuryhomes', '/reviews', '/55-plus', '/condos-townhouses', '/newhomesourcetv', 
               '/manufactured-homes', '/ebook', '/mortgagecalculator', '/professional', '/aboutus', '/reviews', 
               '/leadership-team', '/media-center', '/contactus', '/unsubscribe', '/siteindex', '/termsofuse', 
               '/privacypolicy',  '/guide/','/stateindex/', '/freebrochure/' ]
secondary_pages = ['/community/', '/plandetail/', '/basiccommunity/', '/basicdetail/', '/specdetail/',
                   '/resourcecenter/', '/homedetail/', '/communitydetail/', '/builder/', '/newhomelistings', '/home-builders/']
weired = ['/tucson/', '/modular-homes/', '/condo-sale/', '/mls_com', '/yahoorealestate/', '/newhomebook/', '/mysanantonio/', 
         '/homegain/', '/dallasnews/']
all_pages = primary_pages + quick_links + secondary_pages + weired




def reading_file(files):

    df_raw = pd.DataFrame() 
    for file in files:
        df = pd.read_csv(file, names=columns, encoding = 'cp1256',  sep=r'\s+', low_memory=False)
        df_raw = df_raw.append(df)   
        del df
    df_raw = df_raw[~df_raw['date'].str.startswith('#')]
    df_raw = df_raw[df_raw['cs-host'] == r'www.newhomesource.com']
    df_raw['datetime'] = pd.to_datetime(df_raw['date'] + " " + df_raw['time']) 
    df_raw = df_raw.drop(columns = ['time']).dropna().drop_duplicates().reset_index(drop=True)
    df_raw['uniqueid'] = df_raw['c-ip'] + '_' + df_raw['cs(User-Agent)']
    df_BHI = df_raw[df_raw['c-ip'].str.startswith(tuple(our_ips))]  
    df_raw = df_raw[~df_raw['uniqueid'].isin(df_BHI['uniqueid'].unique().tolist())]

    return df_raw


def create_sessions(df_raw1):

    # creating time_gap of each request made by each user
    df_raw1['time_gap'] = df_raw1.sort_values(['uniqueid', 'datetime']).groupby('uniqueid')['datetime'].diff().fillna(pd.Timedelta(seconds=0))

    #finding users with time_gap more than 1 hour
    delta = datetime.timedelta(hours = 0.5)
    users = df_raw1[df_raw1['time_gap'] > delta]
    users_list = users['uniqueid'].tolist()

    # multi users mean that the user had multiple sessions
    # single users mean that the user had single sessions
    df_multi_users = df_raw1[df_raw1['uniqueid'].isin(users_list)]
    df_single_users = df_raw1[~df_raw1['uniqueid'].isin(users_list)]

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

    sessions = pd.concat([sessionlist, users], axis = 1, sort=False)
    sessionids = sessions.drop('sessioncount', axis = 1)
    sessions_c = sessions[['uniqueid', 'sessioncount']].drop_duplicates()

    df_multi_users = pd.merge(sessionids, df_multi_users, on = ['s-sitename', 's-computername', 's-ip', 'cs-method', 
                                'cs-uri-stem','cs-uri-query', 's-port', 'cs-username', 'c-ip', 'cs-version',
                                'cs(User-Agent)', 'cs(Cookie)', 'cs(Referer)', 'cs-host', 'sc-status','sc-substatus', 
                                'sc-win32-status', 'sc-bytes', 'cs-bytes', 'time-taken','datetime', 'date', 
                                'uniqueid', 'time_gap'], how = 'outer')

    df_multi_users = df_multi_users.sort_values(by = ['uniqueid', 'datetime'])
    df_multi_users = df_multi_users.groupby('uniqueid').ffill()
    p = df_multi_users['uniqueid'] + '_0' 
    df_multi_users['sessionid'] = df_multi_users['sessionid'].fillna(p)

    df_multi_users = pd.merge(df_multi_users, sessions_c, on = 'uniqueid', how = 'outer')

    # Concatenating single and multi users together 
    df_raw1 = pd.concat([df_multi_users, df_single_users], sort=False)
    
    return df_raw1


def features(df):
    
    df = df.drop(['s-port', 'cs-username',  'cs-host', 's-sitename','s-computername', 'cs-uri-query',\
                  's-ip', 'uniqueid', 'time_gap', 'cs-version', 'sc-bytes', 'c-ip', 'sc-substatus', \
                  'sc-win32-status', 'cs-bytes', 'time-taken', 'date'], axis = 1)
    hits = df.groupby('sessionid')['cs-method'].size().reset_index(name='total_hits')
    df = pd.merge(df, hits, on = 'sessionid')
    

    main_stems = df[df['cs-uri-stem'].str.startswith(tuple(all_pages))]
    main_stems = main_stems.groupby('sessionid')['cs-uri-stem'].size().reset_index(name = 'mainStems_count')
    df = df.merge(main_stems, on = 'sessionid', how = 'outer').fillna(0)
    df['mainStems_count'] = round(df['mainStems_count'] / df['total_hits'], 2)  
    
    single_stems = df.groupby('sessionid')['cs-uri-stem'].nunique().reset_index(name='unique_stem_count')
    df = df.merge(single_stems, on='sessionid', how='outer').fillna(0)
    
    refs_count = df.groupby('sessionid')['cs(Referer)'].nunique().reset_index(name='ref_count')
    df = df.merge(refs_count, on='sessionid', how='outer').fillna(0)
 
    unique_cookie = df.groupby('sessionid')['cs(Cookie)'].nunique().reset_index(name = 'unique_cookie_count')
    df = df.merge(unique_cookie, on = 'sessionid', how = 'outer').fillna(0).drop('cs(Cookie)', axis = 1)
    
    active_hours = df.set_index('datetime').groupby('sessionid')['cs-method'].resample('H').count()
    active_hours = active_hours.reset_index().groupby('sessionid')['datetime'].size().reset_index(name = 'active_hours_count')
    df = df.merge(active_hours, on = 'sessionid')

    methods = ['GET', 'HEAD', 'OPTIONS', 'POST']
    for k in methods:
        method_groups = df[df['cs-method'] == k]
        method_groups = method_groups.groupby('sessionid')['cs-method'].count().reset_index(name=k).fillna(0)
        df = df.merge(method_groups, on = 'sessionid', how='outer').fillna(0)

    status = ['2','3','4','5']
    for k in status:
        status_groups = df[df['sc-status'].str.startswith(k)]
        status_groups = status_groups.groupby('sessionid')['sc-status'].count().reset_index(name = k +'00s')
        df = df.merge(status_groups, on='sessionid', how='outer').fillna(0)

    df = df.drop(['cs(Referer)', 'datetime', 'cs-method', 'sc-status'], axis=1)
    
    return df

def cleaning(df):
    
    # removing bot keywords and known bots & defining total hits made in each session  
    df_UserAgents = df['cs(User-Agent)'].unique().tolist()
    bot_users1 = [i for i in df_UserAgents for p in bot_keys if p.lower() in i.lower()]
    bot_users2 = df[~df['cs(User-Agent)'].str.contains(r'[.,-_;:+\/]{5}')]['cs(User-Agent)'].unique().tolist()   
    total_bot_users = bot_users + bot_users1 + bot_users2
    user_agent_based_sessions = df[df['cs(User-Agent)'].isin(total_bot_users)]['sessionid'].unique().tolist()
    df = df.drop(['cs(User-Agent)'], axis=1)
    
    # cleaning based on total hits > 500 and all are get
    get_based_bots = df[(df['total_hits'] >= 200) & \
                     (df['total_hits'] == df['GET'])]['sessionid'].unique().tolist()  
    
    #cleaning based on referers : single referer if total hits>100    
    ref_bots1 = df[(df['total_hits'] >= 100) & (df['ref_count'] <= 2) \
                             ]['sessionid'].unique().tolist()
    ref_bots2 = df[(df['total_hits'] >= 500) & (df['ref_count'] <= 5) \
                             ]['sessionid'].unique().tolist()     
    
    # mainstem based bots
    main_sessions = df[(df['total_hits'] > 3) & (df['mainStems_count'] == 1) \
                              ]['sessionid'].unique().tolist()    
    
    # based on stems
    stem_bots1 = df[(df['total_hits'] > 100) & (df['unique_stem_count'] <= 3)]['sessionid'].unique().tolist()
    stem_bots2 = df[(df['total_hits'] > 1000) & (df['unique_stem_count'] <=10)]['sessionid'].unique().tolist()   
    stem_bots3 = df[df['cs-uri-stem'].str.contains(r'robots|.txt' \
                                                )]['sessionid'].unique().tolist() 
    # all condtional bots
    all_bots = list(set(get_based_bots + ref_bots1 + ref_bots2 + main_sessions + \
                                stem_bots1 + stem_bots2 + stem_bots3 + user_agent_based_sessions))
    
    # final cleaning:
    df = df.drop(['cs-uri-stem'], axis=1).reset_index(drop=True)
    df_clean = df[~df['sessionid'].isin(all_bots)]
    df_bots = df[~df['sessionid'].isin(df_clean['sessionid'].unique().tolist())]    
    df.drop_duplicates('sessionid', keep='first', inplace=True)
          
    return df, df_clean, df_bots


def testing(df, clf1):
    
    y_pred = clf1.predict(df)
    df['pred'] = y_pred    
    bot_logs = df[df['pred'] == 1]    
    return bot_logs


def main():
    filenames = glob.glob(path_to_pick_files_from + '/*{}.log'.format(date))
    if filenames == []:
        print('Files not located! Please try again.')
    print('All files of this date are: ', filenames)

    log_raw = reading_file(filenames)
    log_sessions = create_sessions(log_raw)
    log_features = features(log_sessions)
    
    logs, clean_logs, bot_logs = cleaning(log_features)

    logs1 = logs.drop(['sessionid', 'total_hits'], axis=1)
    model_bot_log = testing(logs1, classifier)
    processed_bots=logs.loc[model_bot_log.reset_index()['index'].tolist()]
    bot_log=pd.concat([bot_logs, processed_bots], sort=False)
    clean_log=log_sessions[~log_sessions['sessionid'].isin(bot_log['sessionid'].unique().tolist())]
    bot_log=log_sessions[log_sessions['sessionid'].isin(bot_log['sessionid'].unique().tolist())]
    print('Bot Classification Done! Working on extracting data now.')
  
    del log_raw
    del log_sessions
    del log_features
    del logs, clean_logs, bot_logs
    del logs1
    del model_bot_log, processed_bots

    return clean_log, bot_log
          


def feature_extraction():

    clean_data, bot_data = main()

    clean_data = clean_data.reset_index(drop=True)
    bot_data = bot_data.reset_index(drop=True)

    users_hits = len(clean_data)
    bots_hits = len(bot_data)
    bots_count = bot_data['uniqueid'].nunique()
    users_count = clean_data['uniqueid'].nunique()

    users_sessions = clean_data['sessionid'].nunique()
    bots_sessions = bot_data['sessionid'].nunique()

    sessions_per_user = round(users_sessions / users_count, 2)
    sessions_per_bot = round(bots_sessions / bots_count, 2)

    one_session_users = clean_data[clean_data['sessioncount'] == 1]['sessionid'].nunique()
    multi_session_users = clean_data[clean_data['sessioncount'] != 1]['sessionid'].nunique()
    one_session_bots = bot_data[bot_data['sessioncount'] == 1]['sessionid'].nunique()
    multi_session_bots = bot_data[bot_data['sessioncount'] != 1]['sessionid'].nunique()

    urls_to_remove = ['service-worker', 'GetAdParameters', 'settvbadge', 'serviceWorkers', 'getimagebrackgrounddata',
                      'gettypeaheadoptions', 'undefined', 'setrefer', 'LocationsIndex', 'manifest.json', 'dynamicadbanner',
                      'GetBrandMarketMapPoints', 'GoogleAnalytics', 'getcommunitymapcards', 'mappopup',
                      'getmediaplayerobjects', 'getlocationbasedinformation', 'getnearbycommunities', 'currentlocation',
                      'GetStaticMapImageUrl', 'mapsearch', 'favicon.ico', 'submittypeaheadsearch', 'sendtophone',
                      '/freebrochure/requestbrochur', 'brochuregen', 'locationhandler', 'conversiontracker',
                      'getbranchimages', 'homepage', 'mysanantonio', 'getmarketpoints', 'logredirect', 'data:image',
                      'undefined', '.php', '.aspx', 'SearchParams', 'eventlogger', 'commconfirm', 'driving', 'directions',
                      'MyBrochure', 'partialviews', 'forgotpasswordmodal', 'mobileredirect', '.xml', '.js', '.jpg', '.png',
                      'thankyoutracker', 'rcomms', 'LocationIndex', 'getfooter', 'get', 'error',
                      'System.Collections.Generic',
                      'quickmoveinsearch']

    get_pages = clean_data[clean_data['cs-method'] == 'GET']
    get_pages = get_pages.copy()
    get_pages['url'] = 0
    get_pages = get_pages[~get_pages['cs-uri-stem'].str.contains(r'|'.join(urls_to_remove), case=False)]
    get_pages.loc[get_pages['cs-uri-query'] == '-', ['url']] = get_pages['cs-uri-stem']
    get_pages.loc[get_pages['cs-uri-query'] != '-', ['url']] = get_pages['cs-uri-stem'] + '?' + get_pages['cs-uri-query']
    pages_per_usersession = round(len(get_pages) / users_sessions, 2)

    get_pages_bot = bot_data[bot_data['cs-method'] == 'GET']
    get_pages_bot = get_pages_bot.copy()
    get_pages_bot = get_pages_bot[~get_pages_bot['cs-uri-stem'].str.contains(r'|'.join(urls_to_remove), case=False)]
    pages_per_botsession = round(len(get_pages_bot) / bots_sessions, 2)

    users_referers_data = clean_data.groupby('sessionid').first().reset_index()
    users_referers_distribution = users_referers_data['cs(Referer)'].str.split('/', expand=True)[2].value_counts()
    users_referers_distribution = users_referers_distribution.to_dict()

    bots_referers_data = bot_data.groupby('sessionid').first().reset_index()
    bots_referers_data = bots_referers_data['cs(Referer)'].str.split('/', expand=True)[2].value_counts()
    bots_referers_data = bots_referers_data.to_dict()

    clean_data['datetime'] = pd.to_datetime(clean_data['datetime'])
    clean_data = clean_data.sort_values(by=['sessionid', 'datetime'])
    first_last_users = clean_data.groupby('sessionid')['datetime'].agg(['first', 'last']).stack().reset_index(name='datetime')
    session_duration_users = first_last_users.groupby('sessionid')['datetime'].diff().dropna().dt.total_seconds()
    session_duration_users = session_duration_users.describe().drop('count').to_dict()

    bot_data['datetime'] = pd.to_datetime(bot_data['datetime'])
    bot_data = bot_data.sort_values(by=['sessionid', 'datetime'])
    first_last_bots = bot_data.groupby('sessionid')['datetime'].agg(['first', 'last']).stack().reset_index(name='datetime')
    session_duration_bots = first_last_bots.groupby('sessionid')['datetime'].diff().dropna().dt.total_seconds()
    session_duration_bots = session_duration_bots.describe().drop('count').to_dict()

    top_20_pages_users = get_pages['url'].value_counts()[:20].to_dict()
    top_20_pages_bots = get_pages_bot['cs-uri-stem'].value_counts()[:20].to_dict()

    session_hour_users = clean_data[['datetime', 'sessionid']]
    session_hour_users['datetime'] = pd.to_datetime(session_hour_users['datetime'])
    session_hour_users.set_index('datetime', inplace=True)
    session_hour_users = session_hour_users.resample('H')['sessionid'].nunique().to_dict()

    session_hour_bots = bot_data[['datetime', 'sessionid']]
    session_hour_bots['datetime'] = pd.to_datetime(session_hour_bots['datetime'])
    session_hour_bots.set_index('datetime', inplace=True)
    session_hour_bots = session_hour_bots.resample('H')['sessionid'].nunique().to_dict()

    clean_data['sc-status'] = clean_data['sc-status'].astype(str)
    errors_500 = clean_data[clean_data['sc-status'].str.startswith('5')]
    errors_500 = errors_500.copy()
    count_5_errors = len(errors_500)

    errors_500['url'] = 0
    errors_500.loc[errors_500['cs-uri-query'] == '-', ['url']] = errors_500['cs-uri-stem']
    errors_500.loc[errors_500['cs-uri-query'] != '-', ['url']] = errors_500['cs-uri-stem'] \
                                                                 + '?' + errors_500['cs-uri-query']
    errors_500 = errors_500.groupby('url')['sc-status'].count().to_dict()

    eventlogger = clean_data[clean_data['cs-uri-stem'].str.contains('eventlogger', case=False)]
    eventlogger = eventlogger['cs-uri-stem'].str.extract("logevent-(\w*)").rename(
                     {0: 'logevents'}, axis=1)['logevents'].value_counts().to_dict()

    hexa = {"%0": "NUL", "%1": "SOH", "%3": "ETX", "%4": "EOT", "%5": "ENQ", "%6": "ACK", "%7": "BEL", "%8": "BS",
            "%9": "TAB", "%A": "LF", "%B": "VT", "%C": "FF", "%D": "CR", "%E": "SO", "%F": "SI", "%10": "DLE",
            "%11": "DC1", "%12": "DC2", "%13": "DC3", "%14": "DC4", "%15": "NAK", "%16": "SYN", "%17": "ETB",
            "%18": "CANCEL", "%19": "EM", "%1A": "SUB", "%1B": "ESC", "%1C": "FS", "%1D": "GS", "%1E": "RS", "%1F": "US",
            "%20": " ", "%21": "!", "%22": r"\\", r"%23": r"#", r"%24": r"$", "%25": "%", "%26": "&",
            "%27": r"\\", r"%28": "(", r"%29": r")", r"%2A": r"*", "%2B": "+", "%2C": ",", "%2D": "-", "%2E": ".",
            "%2F": "/", "%30": "0", "%31": "1", "%32": "2", "%33": "3", "%34": "4", "%35": "5", "%36": "6",
            "%37": "7", "%38": "8", "%39": "9", "%3A": ":", "%3B": ";", "%3C": "<", "%3D": "=", "%3E": ">",
            "%3F": "?", "%40": "@", "%41": "A", "%42": "B", "%43": "C", "%44": "D", "%45": "E", "%46": "F",
            "%47": "G", "%48": "H", "%49": "I", "%4A": "J", "%4B": "K", "%4C": "L", "%4D": "M", "%4E": "N",
            "%4F": "O", "%50": "P", "%51": "Q", "%52": "R", "%53": "S", "%54": "T", "%55": "U", "%56": "V",
            "%57": "W", "%58": "X", "%59": "Y", "%5A": "Z", "%5B": "[", "%5D": "]", "%5E": "^",
            "%5F": "_", "%60": "`", "%61": "a", "%62": "b", "%63": "c", "%64": "d", "%65": "e", "%66": "f",
            "%67": "g", "%68": "h", "%69": "i", "%6A": "j", "%6B": "k", "%6C": "l", "%6D": "m", "%6E": "n",
            "%6F": "o", "%70": "p", "%71": "q", "%72": "r", "%73": "s", "%74": "t", "%75": "u", "%76": "v",
            "%77": "w", "%78": "x", "%79": "y", "%7A": "z", "%7B": "{", "%7C": "|", "%7D": "}", "%7E": "~",
            "%7F": "DEL"}

    questions = clean_data[clean_data['cs-uri-query'].str.contains('Comments=', case=False)]
    questions = questions.replace(hexa, regex=True)
    questions = questions['cs-uri-query'].str.extract("Comments=([a-zA-Z0-9%.\,\+'\/\(\)$\?!*>:;<=_~-]*)"
                                                      ).dropna().rename({0: 'questions'}, axis=1)
    questions = questions.loc[~(questions['questions'] == '')]
    question = questions.drop_duplicates('questions')
    question = question.copy()
    question['questions'] = question['questions'].str.replace('+', ' ')
    questions = question['questions'].unique().tolist()

    scraper_keys = ['.gov', '.com', 'Antivirus', 'BUbiNG', 'Barkrowler', 'Callpod', 'Certificate',
                    'CloudFlare-AlwaysOnline', 'Diagnostics', 'github', 'PycURL', 'curl', 'Ruby'
                    'Dispatch', 'Dorado', 'Drupal', 'EasyBib', 'Extension', 'FeedBurner', 'Go-http-client', 'Grammarly',
                    'HttpClient', 'HubSpot', 'HubSpot+inbound+link+reporting+check', 'Iframely', 'Indexer', 'Java/1.8.0',
                    'Jersey', 'Magic', 'MagpieRSS', 'Professional', 'Yowser', 'spam', 'special_archiver',
                    'Mediapartners', 'MeltwaterNews', 'MetaURI', 'NING', 'POE-Component', 'PTST', 'PageGetter', 'Pcore',
                    'Proxy', 'Qwantify', 'SafariViewService', 'Saleslift', 'Scoop.it', 'ScoutJet', 'SpeedCurve', 'Twisted',
                    'Uzbl', 'WhatsApp', 'Yeti', '__CT_JOB_ID__', 'ad-', 'admantx', 'ahrefs', 'analytics', 'analyze',
                    'antenna', 'archive', 'datamin', 'dataxu',  'mailto', 'riddler', 'package', 'paper', 'wordpress',
                    'bot', 'brain', 'bub', 'check', 'click', 'cloud', 'coc_coc_browser', 'cognitive', 'corpus', 'crawl',
                    'detection', 'exact', 'expo', 'extract', 'favicon', 'feed', 'fetch', 'getintent', 'gooblog',
                    'grapeshot', 'hit', 'httpsearch', 'ichiro', 'intelligence', 'job', 'law', 'linkcheck', 'ltx71',
                    'mapping', 'marketinggrader', 'mediapartner', 'meltwater', 'monitor', 'netseer', 'news', 'okhttp',
                    'parse', 'process', 'proximic', 'ptst', 'python', 'qwant', 'reader', 'researchscan', 'restsharp',
                    'runscope-radar', 'scan', 'scrap', 'screenshot', 'search', 'seeker', 'seo', 'snapshot', 'social',
                    'spider', 'test', 'track', 'traveler', 'trovit', 'ubermetrics', 'um-CC', 'um-FC', 'um-LN', 'walker',
                    'runscope-radar', 'HeadlessChrome', 'PhantomJS', 'CasperJS', 'YaBrowser', 'coccocbot', 'coc_coc',
                    'Electron', 'chromeframe', 'Camino', 'x.x.x', 'Apache-HttpClient', 'libwww', 'perl', 'masscan']

    search_engine_keys = ['Googlebot', 'bingbot', 'adsbot', 'Baiduspider', 'Yandex', 'Sogou', 'AppEngine-Google',
                          'BingPreview', 'facebookexternalhit', 'Pinterestbot', 'Pingdom', 'adidxbot', 'Qwantify',
                          'yahoo-ad-monitoring', 'YandexMobileBot', 'duckduckgo'
                          'Mediapartners-Google', 'GoogleImageProxy', 'Google+Favicon', 'Googlebot-Image',
                          'HeadlessChrome', 'applebot', 'Twitterbot', 'LinkedInBot', 'slurp', 'YaBrowser', 'DeuSu']

    bots_stats = bot_data['cs(User-Agent)'].value_counts()[:30].to_dict()

    bot_data['sc-bytes'] = bot_data['sc-bytes'].astype(int)
    clean_data['sc-bytes'] = clean_data['sc-bytes'].astype(int)
    clean_data['time-taken'] = clean_data['time-taken'].astype(int)
    # bot_data['time-taken'] = bot_data['time-taken'].astype(int)

    total_sc_bytes_bots = round(bot_data['sc-bytes'].sum()/1000, 2)
    total_sc_bytes_users = round(clean_data['sc-bytes'].sum()/1000, 2)

    total_time_bots = round((bot_data['time-taken'].sum()/ 1000)/60, 2)
    total_time_users = round(clean_data['time-taken'].sum()/1000/60, 2)

    top_results = get_pages['cs-uri-stem'].str.split('/', expand=True).rename({2: 'results', 3: 'details'}, axis=1)
    top_states = top_results[~top_results['results'].isin(['', '/', None])]['results'].value_counts()[:20].to_dict()
    top_markets = top_results[~top_results['details'].isin(['', '/', None, 'refer-pt2'])]['details'].value_counts()[:20].to_dict()

    final_dataframe = pd.DataFrame(
        {
            'Date': clean_data['date'].min(), 'Users_TotalHits': [users_hits],
            'Bots_TotalHits': [bots_hits], 'Users_UniqueIdCount': [users_count],
            'Bots_UniqueIdCount': [bots_count], 'Users_SessionsCount': [users_sessions],
            'Bots_SessionsCount': [bots_sessions], 'Users_SingleSessionCount': [one_session_users],
            'Bots_SingleSessionCount': [one_session_bots], 'Users_MultiSessionsCount': [multi_session_users],
            'Bots_MultiSessionsCount': [multi_session_bots], 'Users_SessionsPerUser': [sessions_per_user],
            'Bots_SessionsPerBot': [sessions_per_bot], 'Users_PagesPerSession': [pages_per_usersession],
            'Bots_PagesPerSession': [pages_per_botsession],
            'Users_ReferrersDistribution': [users_referers_distribution],
            'Bots_ReferrersDistribution': [bots_referers_data], 'Users_Top20VisitedPages': [top_20_pages_users],
            'Bots_Top20VisitedPages': [top_20_pages_bots], 'Users_SessionCountPerHour': [session_hour_users],
            'Bots_SessionCountPerHour': [session_hour_bots], 'Users_500ErrorsCount': [count_5_errors],
            'Users_500Errors': [errors_500], 'Users_EventloggersCount': [eventlogger],
            'Users_Questions': [questions], 'Users_SCBytes_Bandwidth(kb)': [total_sc_bytes_users],
            'Bots_SCBytes_Bandwidth(kb)': [total_sc_bytes_bots],
            'Users_TotalTime_Bandwidth(m)': [total_time_users],
             'Users_SessionDuration': [session_duration_users], 'Bots_TotalTime_Bandwidth(m)': [total_time_bots],
            'Bots_SessionDuration': [session_duration_bots], 'Users_TopStatesVisited': [top_states],
            'Users_TopMarketsVisited': [top_markets], 'Bots_Top30': [bots_stats]
        })
    final_dataframe.to_json(r'{}/Logs_Summary_{}.json'.format(path_to_save_files, date), orient='records')

feature_extraction()
print('done!')

   
