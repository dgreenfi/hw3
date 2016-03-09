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

def buildHistogram():
    keys = conn.keys()
    values = conn.mget(keys)
    c = collections.Counter(values)
    z = sum(c.values())
    hist= {k:v/float(z) for k,v in c.items()}
    return hist

@app.route("/")
def histogram():
    h = buildHistogram()
    headers=['Hashtag','Frequecy']
    histogram_list=[[k,h[k]] for k in h]
    histogram_list=[headers]+histogram_list
    return render_template('histogram.html',histogram_data=histogram_list)


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