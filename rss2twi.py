import os, sys, configparser, threading, tweepy, feedparser

posted_urls = []
posted_urls_file = os.path.join(os.path.dirname(sys.argv[0]), ".posted_urls.txt")
twitterkeys = os.path.join(os.path.dirname(sys.argv[0]),  ".twitter.ini")
   
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
    # return
    global posted_urls
    if n['link'] in posted_urls:
        return
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
        posted_urls.append(n['link'])
    except tweepy.TweepError as e:
        print ("error: ", str(e))
        print ("status: ", s)
        if (e.api_code == 187):
            posted_urls.append(n['link'])

def readnews(event1, event2):
    news = feedparser.parse('http://news.tut.by/rss/all.rss')
    event1.set()
    news2 = [{'title':x.title, 'link':x.link[0:x.link.find('?utm_campaign')], 'tm':x.published, 'tags':x.tags} for x in news.entries]
    postnews = [n for n in news2 if not n['link'] in posted_urls]
        
    for n in reversed(postnews):
        spitnews(n)
        twitnews(n)
    event2.set()


def main():
    global posted_urls
    try:
        with open(posted_urls_file,'r') as f:
            s = f.read()
            posted_urls = s.split('\n')    
    except FileNotFoundError:
        pass

    e1 = threading.Event()
    e2 = threading.Event()
    worker = threading.Thread(target=readnews, args=(e1, e2))
    worker.daemon = True
    worker.start()
    if e1.wait(60):
        if e2.wait(60):
            None
    with open(posted_urls_file, 'w') as f:
        f.write('\n'.join(posted_urls[-1000:]))

if __name__ == "__main__":
    main()


