import json
import urllib
import urllib2
from urlparse import urlparse

class News:
    def __init__(self):
        self.size = 0
        self.news_articles = ['https://www.bloomberg.com/politics/articles/2017-03-17/justice-department-responds-to-congress-on-surveillance-sort-of',
                              'https://www.bloomberg.com/politics/articles/2017-03-17/trade-talk-shows-trump-merkel-have-little-common-ground']
        self.news_headings = []
        self.news_bodies = []
        self.diffbot_api_key = 'c19e6ec5802ff6fdde5a483d37851b5e'
        self.timeline = False #change to true when timeline is ready
        self.curr_alpha = 255 * 2.0
        self.curr_news_item = 0
        self.expanded_news = False

    def update_news(self):
        #TODO must call news api. Also request only 5 news articles
        for news_url in self.news_articles:
            data = {}
            data['url'] = news_url
            data['token'] = self.diffbot_api_key

            url_values = urllib.urlencode(data)
            full_url = "https://api.diffbot.com/v3/article?" + url_values
            print(full_url)
            news = json.loads(urllib.urlopen(full_url).read())
            if "error" not in news:
                self.news_headings.append(news["objects"][0]["title"])
                self.news_bodies.append(news["objects"][0]["text"])
        self.size = len(self.news_headings)