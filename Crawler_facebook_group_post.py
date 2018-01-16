'''
실행 명령어
python fb_group_scraper.py <group_id>
Facebook Session timeout 2 hours
get access_token value in the through graph API

Author : NOBIZ - Joshua Park

'''
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime


def request(url):
    """Try to open and read an URL.
    """
    print("url : ", url)
    req = urllib.request.Request(url)
    print("req : ", req.data)
    while True:
        try:
            resp = urllib.request.urlopen(req)
            return resp.read()
        except urllib.error.URLError as err:
            if hasattr(err, 'code') and err.code == 400:
                print('*** Please check the group ID and the access token.\n')
                raise
            print('*** %s. Retrying...' % err)
            time.sleep(5)


def get_group_data():
    """Build the URL to ask for threads and comments data.
    'https://graph.facebook.com/v2.9/%s/feed?fields=id,permalink_url,' Before
    """
    url = ('https://graph.facebook.com/%s/feed?fields=id,permalink_url,'
           'created_time,from,message,type,link,'
           'likes.limit(0).summary(true),'
           'comments{id,created_time,from,message,comment_count,like_count,'
           'attachment,comments{id,created_time,from,message,like_count,'
           'attachment}}&limit=100&access_token=%s' % (GID, TOKEN))

    return json.loads(request(url))


def format_string(text):
    """Format a string in a good way or returns an empty one if input is None.
    """
    if text is None:
        return ''

    return ' '.join(
        text.translate({
            0x2018: 0x27,
            0x2019: 0x27,
            0x201C: 0x22,
            0x201D: 0x22,
            0xA0: 0x20,
            0xA: 0x20,
            0xD: 0x20
        }).split())


def format_date(date, short=True):
    """Format a date in the selected way.
    """
    return date.strftime('%H:%M:%S') if short else \
        date.strftime('%Y-%m-%d %H:%M:%S')


def process_post(post, parent=''):
    """Process the data from a thread or a comment.
    """
    print("process_post.post : ", post.get)
    post_id = post.get('id')
    date = '' if 'created_time' not in post else \
        datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    author = '' if 'from' not in post else \
        format_string(post['from'].get('name'))
    message = format_string(post.get('message'))

    # If it's a thread
    if parent == '':
        parent = format_string(post.get('permalink_url'))
        likes = 0 if 'likes' not in post else \
            post['likes']['summary']['total_count']
        comments = 0 if 'comments' not in post else \
            len(post['comments']['data'])
        kind = format_string(post.get('type'))

        link = format_string(post.get('link'))
        if link != '':
            if message != '':
                message += ' '
            message += '[' + link + ']'

    # If it's a comment
    else:
        likes = post.get('like_count', 0)
        comments = post.get('comment_count', 0)
        kind = 'comment' if 'comment_count' in post else 'subcomment'

        if 'attachment' in post:
            kind += '_' + format_string(post['attachment'].get('type'))

    return (str(post_id),
            str(parent),
            format_date(date, False),
            author,
            message,
            kind,
            likes,
            comments)


def get_comments(thread, output):
    """Get all the comments and subcomments from a thread.
    """
    num_comments = 0
    next_page = True
    comments = thread.get('comments')

    while next_page and comments is not None:
        for comment in comments.get('data', []):
            output.writerow(process_post(comment, thread['id']))

            next_subpage = True
            subcomments = comment.get('comments')

            while next_subpage and subcomments is not None:
                for subcomment in subcomments['data']:
                    output.writerow(process_post(subcomment, comment['id']))
                    num_comments += 1
                if 'paging' in subcomments and 'next' in subcomments['paging']:
                    subcomments = json.loads(request(
                        subcomments['paging']['next']))
                else:
                    next_subpage = False

            num_comments += 1

        if 'paging' in comments and 'next' in comments['paging']:
            comments = json.loads(request(comments['paging']['next']))
        else:
            next_page = False

    return num_comments

# 두번째 호출
def write_csv():
    with open('/home/crawler/kmtc/data/facebook_group_%s_%s.csv' % (GID, datetime.today().strftime("%Y%m%d")), 'w', encoding='utf-8') as file_name:
        output = csv.writer(file_name)
        output.writerow(['id',
                         'ref',
                         'date',
                         'author',
                         'message',
                         'kind',
                         'likes',
                         'comments'])

        next_page = True
        end = False
        num_threads = 0
        num_comments = 0
        threads = get_group_data()
        print("wrtie_csv.get_group_data() : ", threads)

        while next_page and not end:
            for thread in threads['data']:
                output.writerow(process_post(thread))

                num_comments += get_comments(thread, output)
                num_threads += 1

                if num_threads == LIMIT:
                    end = True
                    break
                elif num_threads % 50 == 0:
                    print('(%s) %s threads and %s comments processed' % \
                        (format_date(datetime.now()),
                         num_threads, num_comments))

            if 'paging' in threads and not end:
                threads = json.loads(request(threads['paging']['next']))
            else:
                next_page = False

        return (num_threads, num_comments)

# First Start
def main():
    print('\n(%s) Getting the last %d threads from Facebook group #%s\n' % (format_date(datetime.now()), LIMIT, GID))
    num_threads, num_comments = write_csv()
    print('\n(%s) That\'s all! %s threads and %s comments in total\n' % (format_date(datetime.now()), num_threads, num_comments))

if __name__ == '__main__':
    try:
        GID = sys.argv[1]
        print("GID :", GID)
        SECRET = 'a1189d7e2349c3e6f3fbe3a4693a0cdb'
        APPID = '1972630052972799'
        TOKEN = APPID + '|' + SECRET
        LIMIT = 250
    except (IndexError, ValueError) as err:
        print('\nError: %s' % err)
        print('Usage: %s <group_id> <access_token> [max_threads]' % sys.argv[0])
        sys.exit(2)

    main()