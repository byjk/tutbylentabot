import os, configparser, threading, tweepy, feedparser, sqlite3

configfile = os.path.join(os.path.expanduser("~"), ".tutbylentabot.ini")
twedb = os.path.join(os.path.expanduser("~"), ".tutbylentabot.db")
twitterkeys = os.path.join(os.path.expanduser("~"), ".twitter.ini")

def getlasturl():
    config = configparser.ConfigParser()
    config.read(configfile)
    res = ''
    try:
        res = config["default"]["lasturl"]
    except:
        None
    return res

def setlasturl(url):
    config = configparser.ConfigParser()
    config.read(configfile)
    config["default"] = {"lasturl": url}
    f = open(configfile, "w")
    config.write(f)
    f.close()

def spitnews(n):
    print (n['title'])
    print (n['link'])
    print (n['tm'])
    try:
        if n['tags']:
            print (n['tags'][0]['term'])
    except:
        None
    print ('')


def twitnews(n):
    #return
    config = configparser.ConfigParser()
    config.read(twitterkeys)
    consumer_key = config["api"]["consumer_key"]
    consumer_secret = config["api"]["consumer_secret"]
    access_key = config["api"]["access_key"]
    access_secret = config["api"]["access_secret"]
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    x = ""
    try:
        if n['tags']:
            x =  n['tags'][0]['term'].replace(" ", "").lower()
    except:
        None
    if x:
        s = n['title'] + " #" + x + " " + n['link']
    else:
        s = n['title'] + " " + n['link']
    try:
        api.update_status(status=s)
    except tweepy.TweepError as e:
        print ("error: ", str(e))
        print (access_key)
        print ("status: ", s)


def readnews(event1, event2):
    url = getlasturl()
    print('---', url, '---')
    news = feedparser.parse('http://news.tut.by/rss/all.rss')
    event1.set()
    news2 = [{'title':x.title, 'link':x.link[0:x.link.find('?utm_campaign')], 'tm':x.published, 'tags':x.tags} for x in news.entries]
    postnews = []
    for n in news2:
        if url == n['link']:
            break
        postnews.append(n)
        
    db = sqlite3.connect(twedb)
    q = db.cursor()
    #r = q.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tweets'").fetchone()
    #if not r:
    #    q.execute("create table tweets (id integer primary key, url text)")
    #    db.commit()
    for n in reversed(postnews):
        r = q.execute("SELECT * FROM tweets where url = ?",[n['link']]).fetchone()
        if not r:
          spitnews(n)
          twitnews(n)
          q.execute("INSERT INTO tweets (url) values(?)",[n['link']])
          db.commit()
          setlasturl(n['link'])
    event2.set()
    db.close()


def main():
    e1 = threading.Event()
    e2 = threading.Event()
    worker = threading.Thread(target=readnews, args=(e1, e2))
    worker.daemon = True
    worker.start()
    if e1.wait(60):
        if e2.wait(60):
            None


if __name__ == "__main__":
    main()


