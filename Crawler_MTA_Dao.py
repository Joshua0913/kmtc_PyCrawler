import pymysql

class MtaDao:
    # gncloud MariaDB Connection
    # conn = pymysql.connect(host='192.168.0.55', port=3306, user='crawler', passwd='0221!', db='crawler', charset ='utf8')
    # cur = conn.cursor()
    # cur.execute("use crawler")
    def __init__(self, title, url_link, id, contents):
        self.name = self.__class__.__name__
        self.title = title
        self.url_link = url_link
        self.id = id
        self.contents = contents

    # Table : INSERT INTO THE CR_MTA_BLOGLIST
    def save_MtaBlogList(self, title, url_link):
        try:
            # VirtuaBox MariaDB
            # conn = pymysql.connect(host='192.168.219.135', port=3306, user='crawler', passwd='0221', db='crawler', charset='utf8')
            # Gncloud MariaDB
            conn = pymysql.connect(host='192.168.0.55', port=3306, user='crawler', passwd='0221!', db='crawler', charset='utf8')
            with conn.cursor() as cur:
                sqld = 'INSERT INTO CR_MTA_BLOGLIST (title, url_link, %s) VALUES (%s,%s)'
                cur.execute(sqld, ("0", self.title, self.url_link))
                conn.commit()
        except:
            conn.rollback()
        finally:
            cur.close()
            conn.close()


    # Table : SELECT IN THE CR_MTA_BLOGLIST
    def select_MtaBlogList(self):
        try:
            conn = pymysql.connect(host='192.168.0.55', port=3306, user='crawler', passwd='0221!', db='crawler', charset='utf8')
            with conn.cursor() as cur:
                sqld = "SELECT ID, TITLE, URL_LINK FROM CR_MTA_BLOGLIST WHERE FLAG = '0' and CONTENTS IS NULL"
                cur.execute(sqld)
                print("Data Row Count :[", cur.rowcount, "]")
                rs = cur.fetchall()
                return rs
        finally:
            cur.close()
            conn.close()

    # ID를 조건으로 url_link값이 유니크한 Row를 컨텐츠내용 업데이트
    def update_MtaBlogList_Flag(self, id, contents):
        try:
            conn = pymysql.connect(host='192.168.0.55', port=3306, user='crawler', passwd='0221!', db='crawler', charset='utf8')
            with conn.cursor() as cur:
                sqld = 'UPDATE CR_MTA_BLOGLIST SET CONTENTS = %s, FLAG = "1" WHERE ID = %s'
                cur.execute(sqld, (contents, int(id)))
                conn.commit()
        except:
            conn.rollback()
            print("An error occurred while updating.!!")
        finally:
            cur.close()
            conn.close()
    #def save_MtaBlogDetail(self):
    #def select_MtaBlogDetail():

