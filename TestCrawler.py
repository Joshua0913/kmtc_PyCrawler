'''
실행 명령어
python fb_group_scraper.py <group_id> <access_token> [max_threads]
Facebook Session timeout 2 hours
get access_token value in the through graph API
'''
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

ymd = datetime.today().strftime("%Y%m%d")
print("today :", ymd)