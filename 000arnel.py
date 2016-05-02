#!/usr/bin/env python
import json, praw, requests, wget


print('\n\n')
print('This will download all image from subreddit')
print('\n\n')

# -------------------------------------------------- #

class Reddit(object):
    def __init__(self, subreddit=0, limits=0):
        '''
        This will ask for the subreddit
            
        '''
        self.links = []
        self.subreddit = subreddit
        self.limits = limits

        if self.subreddit == 0:
            self.subreddit = input('Subreddit: ')
        if self.limits == 0:
            self.limits = input('limit: ')

        try:
            self.limits = int(limits)
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
        rm = True
        for y in range(5):
            for x in self.links:
                if 'eroshare' in x: rm = False
                if 'imgur'    in x: rm = False
                if 'gfycat'   in x: rm = False
                if '.jpg'     in x: rm = False
                if '.png'     in x: rm = False
                if '.gif'     in x: rm = False
                if '.gifv'    in x: rm = False
                if rm == True:
                    print('Deleting: ' + x)
                    self.links.remove(x)
                rm = True


    # -------------------------------------------------- #

    def fixerosh(self):
        '''
        This will fix the eroshare links
        '''
        for x in self.links:
            if 'eroshare' in x:
                try:
                    r = requests.get(x)
                    source = r.text
                    if 'mp4' in source:
                        source = source.split('.mp4')[0].split('src="')[-1] + '.mp4'
                        self.links[self.links.index(x)] = source
                    else:
                        self.links[self.links.index(x)] = x.replace('eroshare.com/i/','i.eroshare.com/') + '.jpg'
                    #print(source)
                except:
                    self.links.remove(x)

    # -------------------------------------------------- #

    def fiximgur(self):
        '''
        This will fix imgur links
        '''
        headers = {'Authorization': 'Client-ID 3d8f01808063b93'}

        for x in self.links:
            if 'imgur' in x and '/a/' not in x and '/gallery/' not in x and '.webm' not in x and '.gif' not in x and '.gifv' not in x and '.png' not in x and '.jpg' not in x: #image
                if x[-1] == '/':
                    x1 = x[:-1]
                else:
                    x1 = x
                id = x1.split('/')[-1]
                url = 'https://api.imgur.com/3/image/%s' % id
                print(url)
                r = requests.get(url, headers=headers)
                j = json.loads(r.text)
                try:
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
                url = 'https://api.imgur.com/3/album/%s' % id
                print(url)
                r = requests.get(url, headers=headers)
                j = json.loads(r.text)
                album_name = j['data']['cover']
                images = [x['link'] for x in j['data']['images']]
                try:
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

    def downloadlink(self):
        '''
        This will download links
        '''
        for x in self.links:
            if type(x) != list: #single file
                filename = x.split('/')[-1]
                if not filename in wget.os.listdir('.'):
                    print(' Downloading [%s/%s]: %s' % (self.links.index(x) + 1, len(self.links), x))
                    wget.download(x)
                else:
                    print(' Skipping [%s/%s]: %s' % (self.links.index(x) + 1, len(self.links), x))

            elif type(x) == list: #album
                try:
                    wget.os.mkdir(x[0])
                except:
                    pass
                for y in x[1]:
                    folder = x[0] + '/' 
                    filename = str(x[1].index(y) + 1) + ' - ' + y.split('/')[-1]
                    output = folder + filename
                    if not filename in wget.os.listdir(folder):
                        print(' Downloading [%s] - [%s/%s]: %s' % (x[0], x[1].index(y) + 1, len(x[1]), y))
                        wget.download(y, out=output)
                    else:
                        print(' Skipping [%s] - [%s/%s]: %s' % (x[0], x[1].index(y) + 1, len(x[1]), y))


# links = start()
# removelink(links)
# fiximgur(links)
# fixerosh(links)
