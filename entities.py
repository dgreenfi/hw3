import json
import sys
import redis
import time
import nltk
import re

conn = redis.Redis()

def main():
    last=0
    while 1:
        line = sys.stdin.readline()
        tweet = json.loads(line)
        #limit to only hashtagged tweets
        if 'hashtags' in tweet['entities']:
            #for rate tracking
            if last == 0 :
                last = tweet["time"]
                continue
            delta = tweet["time"] - last
            entities=tweet['entities']['hashtags']
            #outputs the time and hashtag for distribution
            for e in entities:
                t = str(time.time())
                print json.dumps({"time":t, "hashtag":e['text'].lower()})

            t = str(time.time())
            #outputs the time between messages for rate
            print json.dumps({"time":t,"delta":delta})
            sys.stdout.flush()
            last = tweet["time"]








if '_name_'!='main':
    main()