import os, websocket, time, json, configparser, threading, tweepy


geoid = "15800"
url = "ws://www.tut.by/wsapi/online/?lang=rus&geo=" + geoid + "&mtime="
configfile = os.path.join(os.path.expanduser("~"), ".tutbylentabot.ini")
referer = '{"ua":"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"}'


def getlasttimestamp():
    config = configparser.ConfigParser()
    config.read(configfile)
    timestamp = int(time.time()) - 6000
    try:
        timestamp = config["default"]["lasttm"]
    except:
        None
    return int(timestamp)


def setlasttimestamp(timestamp):
    config = configparser.ConfigParser()
    config.read(configfile)
    config["default"] = {"lasttm": timestamp}
    f = open(configfile, "w")
    config.write(f)
    f.close()


def spitnews(n):
    print (n['title'])
    print (n['link'])
    print ('')


def twitnews(n):
    config = configparser.ConfigParser()
    config.read(configfile)
    consumer_key = config["api"]["consumer_key"]
    consumer_secret = config["api"]["consumer_secret"]
    access_key = config["api"]["access_key"]
    access_secret = config["api"]["access_secret"]
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    s = n['title'] + " " + n['link']
    api.update_status(status=s)


def readnews(event1, event2):
    timestamp = getlasttimestamp()
    setlasttimestamp(timestamp)
    ws = websocket.WebSocket()
    u = url + str(timestamp)
    ws.connect(u)
    ws.send(referer)
    result = ws.recv()
    event1.set()
    news = json.loads(result)
    for n in reversed(news):
        t = n['tm'] // 1000;
        if timestamp < t:
            timestamp = t
            spitnews(n)
            twitnews(n)
    print('---')
    ws.close()
    setlasttimestamp(timestamp)
    event2.set()


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


