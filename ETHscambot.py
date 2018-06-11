
from scipy.misc import imread, imshow, imsave, imresize
import numpy as np
import time
import pandas as pd
from twitter import *
import urllib
import pickle



config = {}
execfile("config.py", config)

twitter = Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))


def imdist(imr,imf):  #assume same size already
    diff_float = imr.astype(float)-imf.astype(float)
    norm1 =  np.linalg.norm(diff_float/256)/imf.size
    return(100*norm1)

def get_distance(img,img2):
    real40 = imresize(img, [40,40,3])
    real40_1 = imresize(img, [42,42,3])
    real40_2 = imresize(img, [45,45,3])
    fake40 = imresize(img2, [40,40,3])
    real30 = real40[5:35,5:35, :]
    real30_1 = real40_1[7:37, 7:37,:]
    real30_2 = real40_1[10:40, 10:40,:]
    A = np.asarray([[imdist(real30,fake40[i:30+i,j:30+j, :]) for i in range(10)] for j in range(10)])
    B = np.asarray([[imdist(real30_1,fake40[i:30+i,j:30+j, :]) for i in range(10)] for j in range(10)])
    C = np.asarray([[imdist(real30_2,fake40[i:30+i,j:30+j, :]) for i in range(10)] for j in range(10)])
    return min(A.min(), B.min(),C.min())
    


targets = ['el33th4xor','elonmusk','pierre_rochard','kfeng027','lopp','SatoshiLite','SubstratumNet','theonevortex','IOHK_Charles','ummjackson','woonomic','AmberBaldet']



#Saving the data frame isn't really necessary for basic function, but why waste good data?
cols =['screen_name', 'id', 'text', 'source', 'created_at','favourites_count', 'followers_count', 'profile_image_url_https', 'query']
df = pd.DataFrame(columns = cols)
try : df_old = pd.read_csv('results.csv', sep = '\t', encoding='utf-8')  
except: df_old = df


#Twitter gets mad when you report the same user twice
try:
    with open("reported.pickle", "rb") as fp: 
        reported_users = pickle.load(fp)
except:
    reported_users=[]


#This will stop us from redownloaded files over and over
try:
    with open("downloaded.pickle", "rb") as fp: 
        downloaded_users = pickle.load(fp)
except: 
    downloaded_users = []


#main 
for t in targets:
    print '\n', t, '\n'
    time.sleep(2)
    try : img = imread('images/'+t+'.jpg')
    except: 
        link = 'https://twitter.com/'+t+'/profile_image?size=normal'
        urllib.urlretrieve(link, 'images/'+t+".jpg")
        img = imread(t+'.jpg')
    qu = '@'+t
    query = twitter.search.tweets(q=qu, count=100)   
    for s in query['statuses']:
        df.loc[len(df)] = [s['user']['screen_name'], int(s['id']), s['text'], s['source'], s['created_at'], s['user']['favourites_count'], s['user']['followers_count'], s['user']['profile_image_url_https'], qu ]
    downloaded_users = list(downloaded_users)
    for i in range(len(df)):
        if df.loc[i].screen_name not in downloaded_users:
            urllib.urlretrieve(df.loc[i].profile_image_url_https, 'images/'+df.loc[i].screen_name+".jpg")
            print 'downloaded', df.loc[i].screen_name
            downloaded_users+=[df.loc[i].screen_name]
    downloaded_users = set(downloaded_users)
    df_old = df_old.append(df)
    for s in query['statuses']:
        name = s['user']['screen_name']
        img2 = imread('images/'+name+'.jpg')
        try : dist = get_distance(img,img2)
        except : pass
        print dist
        print name
        if dist<.25:   #This is an arbitrary number that seems to work
            imshow(img2)  #this stops the process so you can visually check the image is a fake 
            text = '@'+name+' tweet ' +str(s['id']) + " created at " + str(s['created_at']) + " high probability bot due to the image similarity metric" + " please report , USER HAS BEEN REPORTED TO TWITTER #ReportBots :)"
            if name == t: continue
            else : 
                if name not in reported_users:
                    twitter.users.report_spam(screen_name = s['user']['screen_name'], perform_block = False)
                    reported_users+=[name]
                    print "reported user:", name
                    twitter.statuses.update(status=text, in_reply_to_status_id = s['id'], auto_populate_reply_metadata=True )
                    twitter.lists.members.create(list_id=LIST_ID, screen_name=name)  #if you haven't created a list, comment this line out
                    with open("reported.pickle", "wb") as fp:   
                        pickle.dump(reported_users, fp)   
    with open("downloaded.pickle", "wb") as fp: 
        pickle.dump(downloaded_users,fp) 


#clean up, save data
df_old.to_csv('results.csv', sep = '\t', encoding='utf-8',  index=False)

with open("reported.pickle", "wb") as fp:   #Pickling
    pickle.dump(reported_users, fp) 

with open("downloaded.pickle", "wb") as fp: 
     pickle.dump(downloaded_users,fp) 



