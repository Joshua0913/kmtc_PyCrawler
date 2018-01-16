'''
title   : Medical tourism Global site...
Site    : http://medicaltourismassociation.com/blog
Author  : Crawling by joshua Park
Date    : 2017.12.11
Content
    Save title and link url of the news list in blog
'''
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Crawler_MTA_Dao import MtaDao
import time

# 드라이버 설정 크롬 or 팬
#driver = webdriver.Chrome('/Users/joshua/chromedriver')
driver = webdriver.PhantomJS('/Users/joshua/phantomjs-2.1.1/bin/phantomjs')

# 암묵적으로 페이지가 전부 로딩이 될때까지의 Term을 명시
driver.implicitly_wait(5)
# 크롬브러우져를 통한 네이버 로그인 예제
# driver.get('https://nid.naver.com/nidlogin.login')
# driver.find_element_by_name('id').send_keys('poohya0913@naver.com')
# driver.find_element_by_name('pw').send_keys('pooh0221!')
# driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
driver.get('http://medicaltourismassociation.com/blog/')
# print(driver.page_source)
html = driver.page_source
print("+========+=========+=========+==========+==========+==========+==========+==========+=========+")
# 변수 설정
cntProp = 2
#bsObj = BeautifulSoup(html, "html.parser")
#list = bsObj.select("div > h2 > a")
xlist = driver.find_elements_by_xpath('//div[@class="post first"]/div[@*]/div[@class="article"]/h2/a')
#aflist = driver.find_elements_by_xpath('//div[@class="post first"]/div[@class="pbd-alp-placeholder-"'+i+'"]/div[@*]/div[@class="article"]/h2/a')
aclick = driver.find_element_by_xpath("//div[@class='post first']/h5[@id='pbd-alp-load-posts']/a")
# DB Connection and save data in the class

# 처음 로딩후 첫페이지 데이터 리스트
'''
for pros in xlist:
    title = pros.text
    urllink = pros.get_attribute("href")
    print("first-title : ", title)
    print("first-urllink : ", urllink)
# 더보기 a링크 클릭
print("aclick.text : ", aclick.text)
aclick.click()
'''
# 처음 페이지에서 리스트 가져오는 함수
def firstData(xlist):
    for pros in xlist:
        title = pros.text
        url_link = pros.get_attribute("href")
        mtaDao = MtaDao(title, url_link, "", "")
        mtaDao.save_MtaBlogList(title, url_link)
    # 더보기 a링크 클릭
    print("aclick.text : ", aclick.text)
    aclick.click()

# 두번째 페이지부터 발생되는 데이터 가져오기
def afterData(cntProp):
    while cntProp < 11:
        cName = "pbd-alp-placeholder-" + str(cntProp)
        print("cName : ", cName)
        aflist = driver.find_elements_by_xpath('//div[@class="post first"]/div[@class="%s"]/div[@*]/div[@class="article"]/h2/a' % cName)
        print("aflist.Length : ", aflist.__len__())
        if aflist.__len__() > 0:
            for af in aflist:
                title = af.text
                url_link = af.get_attribute("href")
                mtaDao = MtaDao(title, url_link, "", "")
                mtaDao.save_MtaBlogList(title, url_link)
                print("af.text : ", title)
                print("af.urllink : ", url_link)
        aclick.click()
        cntProp += 1

# Value Object 의 역할 함수
def setStore(title, url_link):
    print("title : ", title)
    print("url_link : ", url_link)

firstData(xlist)
#aclick.click()
afterData(cntProp)
driver.close()
