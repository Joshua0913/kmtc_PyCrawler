'''
Created by Joshua
2017.12.03
website : http://medicaltourismassociation.com/blog/
Contents : this website is medicalTourism guide document in global
'''
from bs4 import BeautifulSoup
import requests

def get_all_html(url):
    _html = ""
    resp = requests.get(url)
    if resp.status_code == 200:
        _html = resp.text
    return _html

#url = "http://medicaltourismassociation.com/blog"
def parser_news_html(html):
    url = "http://www.medicaltourismassociation.com/en/mta-in-the-news.html"
    html = get_all_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    linkList = list()

    for link in soup.find("div", {"id":"mid-col"}).findAll("a"):
        if 'href' in link.attrs:
            print(link.attrs['href'])

        linkList.append(link.attrs['href'])
    return linkList






