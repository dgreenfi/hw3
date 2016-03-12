import json
import sys
import redis
import time
import requests
from scipy import stats
import numpy as np



conn_prob = redis.Redis(db=2)
conn_ent = redis.Redis(db=3)
conn_prob_alert = redis.Redis(db=4)
conn_ent_alert = redis.Redis(db=5)
conn_hash = redis.Redis(db=6)
api_server='http://127.0.0.1:5000/'

def main():

    while 1:
        ent=requests.get(api_server+'entropy')
        jent=ent.json()
        #creates historical entropy records
        t = str(time.time())
        conn_ent.setex(t, jent['entropy'], 600)
        #creates historical probability records so we can do some basic trend analysis
        prob=requests.get(api_server+'probability_hist')
        pjson=prob.json()
        #needed to flush a couple times to get list format right
        #conn_prob.flushdb()
        for p in pjson:
            print p, pjson[p]
            conn_prob.lpush(p, pjson[p])
        time.sleep(2)

        prob=requests.get(api_server+'probability_hist')
        ent=requests.get(api_server+'entropy_history')
        create_alerts_prob(prob.json())
        create_alerts_ent(ent.json())


def create_alerts_prob(prob):
    ###identify new top hashtag
    values=[]
    #create array of (hashtag,probability) tuples
    hashtags=[(k,prob[k]) for k in prob.keys()]
    hashtags=sorted(hashtags, key=lambda x: x[1],reverse=True)
    just_tags=[h[0] for h in hashtags[0:5]]

    #get prior top 5
    keys = conn_hash.keys()
    if len(keys)>1:
        values = conn_hash.mget(keys)

    if len(values)<5:
        #if top hashtags not set, set them
        for i,hash in enumerate(hashtags[0:5]):
            conn_hash.setex(i,hash[0],120)

    else:
        #compare to previous top 5 and reset
        new=[]
        for h in just_tags:
            if h not in values:
                #if hashtag is new, create and create an alert
                alertstring="New trending hashtag " + h + " has " + str(hashtags[just_tags.index(h)][1]) + " probability."
                t = str(time.time())
                print h,values,alertstring
                conn_prob_alert.set(t,alertstring)
        hashtags_new=zip(keys,values)
        hashtags_new=sorted(hashtags, key=lambda x: x[1],reverse=True)
        for i,hash in enumerate(hashtags_new[0:5]):
            #set new top 5
            conn_hash.setex(i,hash[0],120)





def create_alerts_ent(ent):
    #create alerts when system entropy changes
    t = str(time.time())
    entvals=[e[1] for e in ent]
    if entvals[0]>= max(entvals[1:10]):
        alertstring="Entropy is through the roof. It's at the max value in the last " + str(len(ent[0:10])) + " checks."
        conn_ent_alert.setex(t,alertstring,120)
    pass


if '__name__'!='main':
    main()