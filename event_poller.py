import json
import sys
import redis
import time
import nltk
import re
import requests

conn_prob = redis.Redis(db=2)
conn_ent = redis.Redis(db=3)

def main():
    api_server='http://127.0.0.1:5000/'
    last_entropy=0

    while 1:
        ent=requests.get(api_server+'entropy')
        jent=ent.json()
        conn_ent.setex('entropy', jent['entropy'], 600)
        prob=requests.get(api_server+'probability_hist')
        pjson=prob.json()
        for p in pjson:
            conn_prob.setex(p, pjson[p], 600)
        time.sleep(2)


if '__name__'!='main':
    main()