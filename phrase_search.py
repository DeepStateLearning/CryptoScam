
import time
import pandas as pd
from twitter import *
import urllib
import pickle

LIST_ID = 1005494926589636610 #You need to put the list idea here after you create the list
phrase = "As a thanks for your support *E T H E R E U M*"

config = {}
execfile("config.py", config)

twitter = Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))


phrase = "As a thanks for your support *E T H E R E U M*"
 

list_request = twitter.lists.members(list_id=LIST_ID)
list_names = [p['screen_name'] for p in list_request['users']]


#Twitter gets mad when you report the same user twice
try:
    with open("reported.pickle", "rb") as fp: 
        reported_users = pickle.load(fp)
except:
    reported_users=[]


query = twitter.search.tweets(q=phrase, count=100) 
for s in query['statuses']:
    name = s['user']['screen_name']
    print name
    if name not in list_names:
        twitter.lists.members.create(list_id=LIST_ID, screen_name=name)
        print "updated list"
        list_names+=[name]
    if name not in reported_users:
        twitter.users.report_spam(screen_name = name, perform_block = False) 
        print "reported user" 
        reported_users+=[name]
    time.sleep(1)


with open("reported.pickle", "wb") as fp:   
    pickle.dump(reported_users, fp)  













