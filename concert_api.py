import flask
import redis
import collections
import json
import numpy as np
from flask import request
from flask import render_template

app = flask.Flask(__name__)
conn = redis.Redis(db=0)
conn_rate = redis.Redis(db=1)
conn_prob = redis.Redis(db=2)
conn_ent = redis.Redis(db=3)
conn_prob_alert = redis.Redis(db=4)
conn_ent_alert = redis.Redis(db=5)

def buildHistogram():
    keys = conn.keys()
    if len(keys)>0:
        values = conn.mget(keys)
        c = collections.Counter(values)
        z = sum(c.values())
        hist= {k:v/float(z) for k,v in c.items()}
        return hist

    else:
        return []

def prob_alerts():
    keys = conn_prob_alert.keys()
    if len(keys)>0:
        values = conn_prob_alert.mget(keys)
        tuples=zip(keys, values)
        return tuples
    else:
        return []

def ent_alerts():
    keys = conn_ent_alert.keys()
    values = conn_ent_alert.mget(keys)
    tuples=zip(keys, values)
    return tuples


@app.route("/")
def histogram():
    h = buildHistogram()
    headers=['Hashtag','Frequecy']
    histogram_list=[[k,h[k]] for k in h]
    histogram_list=[headers]+histogram_list
    ps=prob_alerts()
    es=ent_alerts()
    print ps
    es_list=[["Entropy Warning",v,str(k)] for (k,v) in es[0:10]]
    table_list=[["Trending Hashtag",v,str(k)] for (k,v) in ps[0:10]]
    table_list=table_list+es_list
    #table_list=[['New Hashtag','Test Tag','10:30'],['Trending Hashtag','#Trending','10:29']]
    hashtag_list=[['#Coolshow',23,{'v':18.5,'f':'18.5%'}],['#Badshow',54,{'v':11.5,'f':'9.5%'}]]
    return render_template('histogram.html',histogram_data=histogram_list,table_data=table_list,hashtag_data=hashtag_list)

@app.route("/histo")
def show_histogram():
    h = buildHistogram()
    return json.dumps(h)

@app.route("/entropy")
def entropy():
    h = buildHistogram()
    entropy= -sum([p*np.log(p) for p in h.values()])
    print entropy
    return json.dumps({"entropy":str(entropy)})

@app.route("/probability")
def probability():
    keys = conn.keys()
    values = conn.mget(keys)

    #hashtag = request.args.get('hashtag')
    #d = conn.get(hashtag)
    return values[0]+keys[0]

@app.route("/probability_hist")
def probability_hist():
    # return current probability distribution for hashtags
    h = buildHistogram()
    print h
    return json.dumps({"prob_hist":h})

@app.route("/probability_curve")
def probability_curve():
    # return curve of historical probability for a given term
    conn_prob = redis.Redis(db=2)
    h = buildHistogram()
    resp={}
    for k in h.keys():
        #range doesn't seem to be working, will limit in
        hist=conn_prob.lrange(k,0,-30)
        #limit to 30 results
        resp[k]=hist[0:30]
    return json.dumps(resp)

@app.route("/entropy_history")
def entropy_history():
    # return array of historical entropites for a distribution
    keys = conn_ent.keys()
    #print keys
    values = conn_ent.mget(keys)
    return json.dumps(sorted(zip(keys,values), key=lambda x: x[0]))


@app.route("/rate")
def rate():
    #return rate in time between messages
    keys = conn_rate.keys()
    numrec=request.args.get('numrec')
    if numrec is None:
        numrec=10

    values = conn_rate.mget(keys)
    deltas=[]
    try:
        deltas = [float(v) for v in values]
    except TypeError:
        pass

    if len(deltas)>=numrec:
        rate = sum(deltas)/float(len(deltas))
    else:
        rate = 0


    return json.dumps({'rate':rate})




if __name__ == "__main__":
    app.debug = True
    app.run()