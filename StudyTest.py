# -*- coding: utf8 -*-

import sys
import urllib.request
import json
import datetime
import csv
import time
import codecs

app_id = "1972630052972799"
app_secret = "a1189d7e2349c3e6f3fbe3a4693a0cdb"
access_token = app_id + "|" + app_secret
print("access_token : ", access_token)
jsonResult = []
jsonData = []


def request_until_succeed(url):
    req = urllib.request.Request(url)
    print("request_until_succeed.req : ", req.get_full_url())
    success = False
    while success is False:
        try:
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)
            print("Error for URL %s: %s" % (url, datetime.datetime.now()))
            print("Retrying.")

    return response.read().decode('utf-8')

# 사이트를 방문하여 직접 ID값 구함. 아래의 함수는 재확인이 필요함.
def getFacebookNumericID(page_id, access_token):
    base = "https://graph.facebook.com/v2.9"
    node = "/" + page_id
    parameters = "/?access_token=%s" % access_token
    url = base + node + parameters
    print("++++++++++++++++++++++++++++++++++++++++")
    print("getFacebookNumericID.url : ", url)
    req = urllib.request.Request(url)
    success = False
    while success is False:
        try:
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            break

    if (success == True):
        data = json.loads(response.read().decode('utf-8'))
        return data['id'];

    return ''


def getFacebookPageFeedData(page_id, access_token, num_statuses, from_date, to_date):
    #base = "https://graph.facebook.com/v2.6"
    base = "https://graph.facebook.com/v2.9"
    node = "/%s/posts" % page_id
    #fields = "/?fields=message(x),link,created_time(x),type(x),name,id," + \
    #         "comments.limit(0).summary(true),shares(x),reactions" + \
    #         ".limit(0).summary(true)"
    fields = "/?fields=message,link,created_time,name,id"
    duration = "&since=%s&until=%s" % (from_date, to_date)
    parameters = "&limit=%s&access_token=%s" % (num_statuses, access_token)
    url = base + node + fields + duration + parameters
    print("getFacebookPageFeedData.url : >> ", url)
    data = json.loads(request_until_succeed(url))

    return data


def getReactionsForStatus(status_id, access_token):
    base = "https://graph.facebook.com/v2.9"
    node = "/%s" % status_id
    reactions = "/?fields=" \
                "reactions.type(LIKE).limit(0).summary(total_count).as(like)" \
                ",reactions.type(LOVE).limit(0).summary(total_count).as(love)" \
                ",reactions.type(WOW).limit(0).summary(total_count).as(wow)" \
                ",reactions.type(HAHA).limit(0).summary(total_count).as(haha)" \
                ",reactions.type(SAD).limit(0).summary(total_count).as(sad)" \
                ",reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
    parameters = "&access_token=%s" % access_token
    url = base + node + reactions + parameters

    data = json.loads(request_until_succeed(url))

    return data


# Needed to write tricky unicode correctly to csv
def unicode_normalize(text):
    return text.translate({0x2018: 0x27, 0x2019: 0x27, 0x201C: 0x22, 0x201D: 0x22,
                           0xa0: 0x20})


def get_num_total_reactions(reaction_type, reactions):
    if reaction_type not in reactions:
        return 0
    else:
        return reactions[reaction_type]['summary']['total_count']


def processFacebookPageFeedStatus(status, access_token):
    status_id = status['id']
    status_message = '' if 'message' not in status.keys() else unicode_normalize(status['message'])
    link_name = '' if 'name' not in status.keys() else unicode_normalize(status['name'])
    status_link = '' if 'link' not in status.keys() else unicode_normalize(status['link'])
    status_type = status['type']

    # Facebook은 기본적으로 UTC를 사용한다. EST = UTC + 9(한국시간)
    status_published = datetime.datetime.strptime(status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + datetime.timedelta(hours=+9)
    status_published = status_published.strftime('%Y-%m-%d %H:%M:%S')

    num_reactions = 0 if 'reactions' not in status else status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else status['shares']['count']

    # 2016-02-24 Facebook에서는 LIKE 이외에 감정을 나타내는 상태를 추가하였음
    # http://newsroom.fb.com/news/2016/02/reactions-now-available-globally/

    reactions = getReactionsForStatus(status_id, access_token) if status_published > '2016-02-24 00:00:00' else {}

    num_likes = 0 if 'like' not in reactions else reactions['like']['summary']['total_count']
    num_likes = num_reactions if status_published < '2016-02-24 00:00:00' else num_likes

    num_loves = get_num_total_reactions('love', reactions)
    num_wows = get_num_total_reactions('wow', reactions)
    num_hahas = get_num_total_reactions('haha', reactions)
    num_sads = get_num_total_reactions('sad', reactions)
    num_angrys = get_num_total_reactions('angry', reactions)

    jsonData.append(
        {'status_id': status_id, 'status_message': status_message, 'link_name': link_name, 'status_link': status_link,
         'status_published': status_published, 'num_reactions': num_reactions, 'num_comments': num_comments,
         'num_shares': num_shares, 'num_likes': num_likes, 'num_loves': num_loves, 'num_wows': num_wows,
         'num_hahas': num_hahas, 'num_sads': num_sads, 'num_angrys': num_angrys})

    return (status_id, status_message, link_name, status_type, status_link,
            status_published, num_reactions, num_comments, num_shares,
            num_likes, num_loves, num_wows, num_hahas, num_sads, num_angrys)


def scrapeFacebookPageFeedStatus(fb_id, page_id, access_token, from_date, to_date):
    with open('%s_facebook_statuses.csv' % fb_id, 'w', newline='') as file:
        w = csv.writer(file)
        w.writerow(["status_id", "status_message", "link_name", "status_type",
                    "status_link", "status_published", "num_reactions",
                    "num_comments", "num_shares", "num_likes", "num_loves",
                    "num_wows", "num_hahas", "num_sads", "num_angrys"])

        has_next_page = True
        num_processed = 0  # keep a count on how many we've processed
        scrape_starttime = datetime.datetime.now()

        print("Scraping %s Facebook Page: %s\n" % (page_id, scrape_starttime))

        statuses = getFacebookPageFeedData(page_id, access_token, 100, from_date, to_date)

        while has_next_page:
            for status in statuses['data']:

                if 'reactions' in status:
                    w.writerow(processFacebookPageFeedStatus(status, access_token))

                num_processed += 1

                if num_processed % 100 == 0:
                    print("%s Statuses Processed: %s" % (num_processed, datetime.datetime.now()))

            if 'paging' in statuses.keys():
                statuses = json.loads(request_until_succeed(statuses['paging']['next']))
            else:
                has_next_page = False

        print("\nDone!\n%s Statuses Processed in %s" % (num_processed, datetime.datetime.now() - scrape_starttime))


if __name__ == '__main__':

    # fb_id = 'nytimes'
    # fb_id = 'jtbnews'
    # fb_id = 'TheNorthFaceKR'
    # fb_id = 'mark.lee.7796'
    '''
    if len(sys.argv) < 4:
        print ("FaceBook ID : ")
        fb_id = input()

        print ("Search Start Date(YYYY-mm-DD) :")
        from_date = input()

        print ("Seach End Data(YYYY-mm-DD) : ")
        to_date = input()
    else:
        fb_id = sys.argv[1];
        from_date = sys.argv[2];
        to_date = sys.argv[3];
    '''
    fb_id = 'poohya0913'
    from_date = '2017-01-01'
    to_date = '2017-12-30'

    #page_id = getFacebookNumericID(fb_id, access_token)
    page_id = '834093761'

    if (page_id == ''):
        print("Couldn't find Numeric ID")
    else:
        scrapeFacebookPageFeedStatus(fb_id, page_id, access_token, from_date, to_date)
        jsonResult.append({'fb_id': fb_id, 'page_id': page_id, 'data': jsonData})

        with open('%s_facebook_statuses.json' % fb_id, 'w') as fp:
            fp.write(json.dumps(jsonResult, sort_keys=False, indent=4, ensure_ascii=False))

