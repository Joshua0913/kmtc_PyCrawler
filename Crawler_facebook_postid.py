import facebook
# 생성한 액세스 토큰을 인수로 전달하고 객체를 돌려 받습니다.
obj = facebook.GraphAPI(access_token="1972630052972799|a1189d7e2349c3e6f3fbe3a4693a0cdb")
postid = str(input("포스트 아이디를 입력하세요 : "))
userid = input("찾으실 유저의 이름을 입력하세요 : ")
response = obj.get_connections(id=postid, connection_name="comments", limit=1000)
_find = []
while response["data"]:
    for data in response["data"]:
        try:
            if userid == data["from"]["name"]:
                _data = {}
                _data["id"] = data["from"]["id"]
                _data["name"] = data["from"]["name"]
                _data["created_time"] = data["created_time"]
                _data["message"] = data["message"]
                _find.append(_data)
        except UnicodeEncodeError as e:
            if userid == data["from"]["name"]:
              _data = {}
              _data["id"] = data["from"]["id"]
              _data["name"] = data["from"]["name"]
              _data["created_time"] = data["created_time"]
              _data["message"] = data["message"]
              _find.append(_data)
    if "paging" in response and "after" in response["paging"]["cursors"]:
        after = response["paging"]["cursors"]["after"]
        response = obj.get_connections(id=postid, connection_name="comments", limit=1000, after=after)
    else:
        break
f = open("/Users/joshua/Documents/facebook_comment.txt", "w")
for data in _find:
    f.write("==" * 30 + "\n")
    f.write(str(data["created_time"]) + "\n")
    f.write(str(data["message"]) + "\n")
    f.write(str(data["id"]) + "\n")
    f.write(str(data["name"]) + "\n")
    f.write("==" * 30 + "\n")
f.close()