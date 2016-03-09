import json
import sys
import redis
import time
import nltk
import re

conn = redis.Redis()
def main():
    while 1:
        stopwords=['concert','been']
        line = sys.stdin.readline()
        tweet = json.loads(line)
        try:
            text = tweet["text"].lower()
        except KeyError as e:
            #bypass system messages
            continue

        #NLTK tokenize seems to be splitting @ and name...trying my own tokenizer
        tokens= nltk.word_tokenize(text)
        tokens= add_users(tokens)
        #print tokens
        #tokens=clean_text(tokens)
        tagged=nltk.pos_tag(tokens)
        bigrams = nltk.bigrams(tagged)
        propers=[]
        #add unigrams
        for tag in tagged:
            if tag[1]=='NNP' or tag[1]=='NNPS':
                if word_qualify(tag[0],stopwords):
                    propers.append(tag[0])
        #add bigrams - maybe
        for b in bigrams:
            if b[0][1]=='NNP'and b[1][1]=='NNP':
                propers.append(b[0][0]+' '+b[1][0])

        t = str(time.time())
        for p in propers:
            print json.dumps({"time":t, "propers":p})
        sys.stdout.flush()

def add_users(tokens):
    new_tokens=[]
    add_next=0
    for i,token in enumerate(tokens):
        if token==chr(64):
            add_next=1
        else:
            new_tokens.append(add_next*'@'+token)
            add_next=0

    return new_tokens

def clean_text(text_list):
    print text_list
    #get rid of special chars and lowercase tokens
    for i,string in enumerate(text_list):
        temp=string.encode("utf8","ignore")
        text_list[i]=''.join(e for e in temp if e.isalnum())
    return text_list

def word_qualify(word,stopwords):
    if word not in stopwords:
        if word !=chr(64):
        #if set('[~!@#$%^&*()_+{}":;\']+$').intersection(word)==0:
            return 1


if '_name_'!='main':
    main()