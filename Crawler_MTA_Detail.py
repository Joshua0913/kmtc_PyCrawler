'''
title   : Medical tourism Global site...
Site    : http://medicaltourismassociation.com/blog + url_link
Author  : Crawling by joshua Park
Date    : 2017.12.11
Content
    connect Saved url and save articles
'''
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Crawler_MTA_Dao import MtaDao
import time
import re

driver = webdriver.PhantomJS('/Users/joshua/phantomjs-2.1.1/bin/phantomjs')
driver.implicitly_wait(5)
title = ""
url_link = ""
mtaDao = MtaDao(title, url_link, "", "")
xlist = mtaDao.select_MtaBlogList()

def updateContents(xlist, driver):
    for dataRow in xlist:
        id = dataRow[0]
        title = dataRow[1]
        url_link = dataRow[2]
        driver.get(url_link)
        html = driver.find_element_by_xpath('//div[@class="eight columns"]')
        contents = html.text
        updateDao = MtaDao("", "", id, contents)
        mtaDao.update_MtaBlogList_Flag(id, contents)

updateContents(xlist, driver)