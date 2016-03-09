import tweepy
import json
import sys
import time

class StdOutListener(tweepy.StreamListener):
    #pass redis connection to connector


    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        tweet = json.loads(data)
        tweet['time'] = time.time()
        if tweet['entities']['hashtags']:
            print json.dumps(tweet)
            sys.stdout.flush()

    def on_error(self, status):
        print status


def open_twitter(args,creds):
    #open a stream to twitter based on keyword arguments
    l = StdOutListener()
    auth = tweepy.OAuthHandler(creds['twitter_key'], creds['twitter_secret'])
    auth.set_access_token(creds['twitter_access_token'], creds['twitter_token_secret'])
    stream = tweepy.Stream(auth, l)
    #subscribe to terms on stream
    stream.filter(track=args['terms'],languages=['en'])

    return l
    #return a connection


def load_creds(credloc):
    #load keys from key file
    with open(credloc) as data_file:
        data = json.load(data_file)
    return data

def main():
    #load credentials
    creds=load_creds('./cred/keys.txt')
    #set search terms for stream
    args={"terms":["concert"]}
    #open connection
    conn=open_twitter(args,creds)

if '__name__'!='main':
    main()