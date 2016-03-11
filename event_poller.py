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
        for p in pjson['prob_hist']:
            print p, pjson['prob_hist'][p]
            conn_prob.lpush(p, pjson['prob_hist'][p])
        time.sleep(2)

        prob=requests.get(api_server+'probability_curve')
        ent=requests.get(api_server+'entropy_history')
        create_alerts_prob(prob.json())
        create_alerts_ent(ent.json())

def create_alerts_prob(prob):

    for k in prob:
        #last minute of probabilitie
        trend=[(100*float(x)) for x in prob[k][0:30]]
        print trend
        y=range(0,len(trend))
        y.reverse()
        if len(trend)>10:
            #note used yet
            slope, intercept, r_value, p_value, std_err = stats.linregress(trend,y)
            #set threshold
            if trend[0]>.1:
                    t = str(time.time())
                    alertstring=k+ " seems to be trending with a probability of " + str(trend[0])
                    conn_prob_alert.set(t,alertstring)

            #system is setup to do more complex regression of trends but still need to add in
        else:
            pass


def create_alerts_ent(ent):
    t = str(time.time())
    if ent[0]== max(ent[0:20]):

        alertstring="Entropy is through the roof. It's at the max value in the last " + str(len(ent[0:20])) + " checks."
        conn_ent_alert.set(t,alertstring)
    pass


if '__name__'!='main':
    main()