#!/usr/bin/env python
import json, praw, requests, wget
from bs4 import BeautifulSoup



class Reddit(object):
    def __init__(self, subreddit=0, limits=0):
        '''
        This will ask for the subreddit
            
        '''
        self.links        = []
        self.deletedlinks = []
        self.subreddit    = subreddit
        self.limits       = limits

        if self.subreddit == 0:
            self.subreddit = input('Subreddit: ')
        if self.limits == 0:
            self.limits = input('limit: ')

        try:
            self.limits = int(self.limits)
            if self.limits == 0:
                self.limits = 20
        except:
            self.limits = 20

        print( 'Fetching %s...[%s]' % (self.subreddit, self.limits))
        self.r = praw.Reddit(user_agent='script')
        self.sub = self.r.get_subreddit(self.subreddit).get_hot(limit=self.limits)
        self.links = [x.url for x in self.sub]
        
        Reddit.removelink(self)


    def fixgfycat(self, links = 0):
        '''
        This will fix gfycat links
        '''
        if links == 0:
            links = self.links[:]

        for x in links:
            if 'gfycat' in x and not any(y in x for y in ['mp4','gif','webm','gifv', 'giant']):
                try:
                    print('Processing:', x)
                    link = x.replace('gfycat.com/', 'gfycat.com/cajax/get/')
                    r = requests.get(link)
                    j = json.loads(r.text)
                    links[links.index(x)] = j['gfyItem']['mp4Url']

                except:
                    print('remove:', x)
                    links.remove(links.index(x))
        return links
