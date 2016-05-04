#!/usr/bin/env python
import json, praw, requests, wget
from bs4 import BeautifulSoup


print('\n\n')
print('This will download all image from subreddit')
print('\n\n')

# -------------------------------------------------- #

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

    def __str__(self):
        return ('\n').join(self.links)
    # -------------------------------------------------- #

    def checklinks(self):
        '''
        This will check and remove all links
        '''
        for x in links:
            print('checking: ' + x)
            r = requests.get(x)
            code = r.status_code
            if '404' in str(code):
                print(x + ' is not working')
                links.remove(x)
        return links

    # -------------------------------------------------- #

    def removelink(self):
        '''
        This will remove links not:
        eroshare, imgur, gfycat, and not .jpg
        '''
        validlinks = ['eroshare','imgur', 'gfycat','.jpg','.png','.gif','.gifv']

        for y in range(5):
            for x in self.links:
                if not any(y in x for y in validlinks):
                    print ('delete: ' + x)
                    self.deletedlinks.append(x)
                    self.links.remove(x)
        self.links = list(set(self.links))

    # -------------------------------------------------- #

    def fixerosh(self):
        '''
        This will fix the eroshare links
        '''
        for x in self.links:
            imagelist = []
            mp4list = []
            if 'eroshare' in x and 'mp4' not in x and 'jpg' not in x:
                print('processing:', x)

                try:
                    r = requests.get(x)
                    source = r.text
                    soup = BeautifulSoup(source, 'html.parser')

                    if 'mp4' in source:
                        soup1 = soup.find_all('div')[0].find_all('source', {'data-default':'true'})
                        mp4list = [y.get('src') for y in soup1]
                        if len(mp4list) > 1:
                            album_name = x.split('/')[-1]
                            self.links[self.links.index(x)] = [album_name, mp4list]
                        else:
                            self.links[self.links.index(x)] = mp4list[0]

                    elif 'jpg' in source:
                        for y in soup.find_all('div', {'class':'blurred-bg'}):
                            imagelist.append('https://' + str(y).split('//')[1][:-10])
                        if len(imagelist) > 1:
                            album_name = x.split('/')[-1]
                            self.links[self.links.index(x)] = [album_name, imagelist]
                        else:
                            self.links[self.links.index(x)] = imagelist[0]

                    else:
                        self.links.remove(x)
                except:
                    print('remove:', x)
                    self.links.remove(x)
           

    # -------------------------------------------------- #

    def fix500px(self):
        '''
        This will fix 500px links
        '''
        for x in self.links:
            print(x)
            if '500px' in x:
                try:
                    print('Processing:', x)
                    r = requests.get(x)
                    source = r.content.decode('utf8')
                    soup = BeautifulSoup(source, 'html.parser')
                    img = soup.find_all('meta', {'property': 'og:image'})[0].get('content')
                    self.links[self.links.index(x)] = str(img)
                except:
                    print('remove:', x)
                    self.links.remove(self.links.index(x))
        pass

    # -------------------------------------------------- #
    def fixgfycat(self):
        '''
        This will fix gfycat links
        '''

        for x in self.links:
            if 'gfycat' in x and not any(y in x for y in ['mp4','gif','webm','gifv', 'giant']):
                try:
                    print('Processing:', x)
                    link = x.replace('gfycat.com/', 'gfycat.com/cajax/get/')
                    r = requests.get(link)
                    j = json.loads(r.text)
                    self.links[self.links.index(x)] = j['gfyItem']['mp4Url']

                except:
                    print('remove:', x)
                    self.links.remove(self.links.index(x))


    # -------------------------------------------------- #
    def fiximgur(self):
        '''
        This will fix imgur links
        '''
        headers = {'Authorization': 'Client-ID 3d8f01808063b93'}

        validlinks = ['.webm','.gif','.gifv','.png','.jpg']
        imguralbum = ['/a/','/gallery/']
        for x in self.links:
            if 'imgur'in x and \
                    not any(x.endswith(y) for y in validlinks) and \
                    not any(y in x for y in imguralbum):
                if x[-1] == '/':
                    x1 = x[:-1]
                else:
                    x1 = x
                id = x1.split('/')[-1]
                if '.' in id:
                    id = id.split('.')[0]
                url = 'https://api.imgur.com/3/image/%s' % id
                print('image processing:', url)

                try:
                    r = requests.get(url, headers=headers)
                    j = json.loads(r.text)
                    self.links[self.links.index(x)] = j['data']['link']

                except:
                    print('image remove:',x)
                    self.links.remove(x)

            elif 'imgur' in x and ('/a/' in x or '/gallery/' in x): #album
                if x[-1] == '/':
                    x1 = x[:-1]
                else:
                    x1 = x
                id = x1.split('/')[-1]
                if '.' in id:
                    id = id.split('.')[0]
                url = 'https://api.imgur.com/3/album/%s' % id
                print('album processing:', url)

                try:
                    r = requests.get(url, headers=headers)
                    j = json.loads(r.text)
                    album_name = j['data']['cover']
                    images = [x['link'] for x in j['data']['images']]
                    self.links[self.links.index(x)] = [album_name, images]

                except:
                    print('album remove:',x)
                    self.links.remove(x)

            elif 'imgur' in x and ('gif' in x or '.gifv' in x or '.webm' in x): #imgur gifv
                if 'gifv' in x:
                    self.links[self.links.index(x)] = x.replace('.gifv', '.mp4')
                elif 'gif' in x:
                    self.links[self.links.index(x)] = x.replace('.gif', '.mp4')
                elif 'webm' in x:
                    self.links[self.links.index(x)] = x.replace('.webm', '.mp4')
            else:
                pass
    
    # -------------------------------------------------- #

    def downloadlink(self, links=0):
        '''
        This will download links
        '''
        if links == 0:
            links = self.links
        try:
            wget.os.mkdir('./Reddit')
        except:
            pass
        for x in self.links:

            filelists = sum([z for x,y,z in wget.os.walk('Reddit')], []) #get all file list and flat list

            if type(x) != list: #single file
                filename = x.split('/')[-1]
                if not filename in filelists:
                    try:
                        wget.os.mkdir('./Reddit/- new/')
                    except:
                        pass

                    try:
                        wget.os.mkdir('./Reddit/- new/' + self.subreddit)
                    except:
                        pass

                    print(' Downloading [%s/%s]: %s' % (self.links.index(x) + 1, len(self.links), x))
                    try:
                        wget.download(x, out='Reddit/- new/%s/%s' % (self.subreddit, filename))
                    except:
                        print(' ERROR - Skipping [%s/%s]: %s' % (self.links.index(x) + 1, len(self.links), x))
                else:
                    print(' Skipping [%s/%s]: %s' % (self.links.index(x) + 1, len(self.links), x))

            elif type(x) == list: #album
                for y in x[1]:
                    folder = './Reddit/- new/' + self.subreddit + '/' + x[0] + '/' 
                    filename = str(x[1].index(y) + 1) + ' - ' + y.split('/')[-1]
                    output = folder + filename
                    if not filename in filelists:

                        try:
                            wget.os.mkdir('./Reddit/- new/')
                        except:
                            pass
                        try:
                            wget.os.mkdir('./Reddit/- new/' + self.subreddit)
                        except:
                            pass
                        try:
                            wget.os.mkdir('./Reddit/- new/' + self.subreddit + '/' + x[0])
                        except:
                            pass

                        print(' Downloading [%s] - [%s/%s]: %s' % (x[0], x[1].index(y) + 1, len(x[1]), y))
                        try:
                            wget.download(y, out=output)
                        except:
                            print(' ERROR - Skipping [%s] - [%s/%s]: %s' % (x[0], x[1].index(y) + 1, len(x[1]), y))
                    else:
                        print(' Skipping [%s] - [%s/%s]: %s' % (x[0], x[1].index(y) + 1, len(x[1]), y))

    def download(*args):
        
        if len(args) < 1:
            self.downloadlink()
        elif 'imgur' in args:
            imgurlink = self.fiximgur()




# links = start()
# removelink(links)
# fiximgur(links)
# fixerosh(links)
arnel = Reddit()