import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import requests, json, random, uuid, sqlite3,time, string, re, traceback,pytz
from threading import Thread
import http.client
http.client._MAXHEADERS = 1000
from http.client import REQUEST_TIMEOUT
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from datetime import datetime,timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from itertools import chain
from dotenv import load_dotenv



parent_folder = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(parent_folder, '.env')
logs_file = os.path.join(parent_folder,'app.log')
arbs_file = os.path.join(parent_folder,'arb.log')

load_dotenv(env_path)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') 
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
TELEGRAM_BOT_NAME = os.getenv('TELEGRAM_BOT_NAME')
