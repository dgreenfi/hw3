
import json
import sys
import redis


conn = redis.Redis(db=0)
conn_delta = redis.Redis(db=1)

while 1:
    line = sys.stdin.readline()
    ljson = json.loads(line)
    print ljson
    if 'delta' not in ljson.keys():
        conn.setex(ljson['time'], ljson['hashtag'], 600)
    else:
        conn_delta.setex(ljson['time'], ljson['delta'], 600)



