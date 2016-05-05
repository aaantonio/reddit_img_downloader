import praw, requests, wget, json
from bs4 import BeautifulSoup

class Reddit(object):

    def __init__(self, subreddit=0, limits=0):

        self.subreddit = subreddit
        self.limits = limits

        self.deletedlinks = []
        self.imgurlinks = []
        self.eroshlinks = []
        self.gfycatlinks = []

        self.origlinks = self.getsubreddit(self.subreddit, self.limits)

        self.links = self.origlinks[:]
        self.removelink()

    def getsubreddit(self, subreddit=0, limits=0):

        if subreddit == 0:
            try:
                subreddit = input('Subreddit: ')
                r = praw.Reddit(user_agent='Script')

                if limits == 0:
                    try:
                        limits = input('Limits: ')
                        limits = int(limits)
                    except:
                        limits = 20

                print('Fetching: %s [%s]' % (subreddit, limits))
                self.limits = limits
                self.subreddit = subreddit
                sub = r.get_subreddit(subreddit).get_hot(limit=limits)
                links = [x.url for x in sub]

            except:
                print('\n\nPlease try another subreddit\n')
                return self.getsubreddit()

        self.links       = links
        self.origlinks   = self.links[:]
        return links


    def removelink(self, links = 0):
        '''
        This will remove links not: eroshare, imgur, gfycat, and not .jpg
        '''
        self.deletedlinks = []

        if links == 0:
            links = self.links

        validlinks = [
                    'eroshare',
                    'imgur',
                    'gfycat',
                    '.jpg',
                    '.png',
                    '.gif',
                    '.gifv']

        i = 0
        while i <= 10:
            for x in links:
                if not any(y in x for y in validlinks):
                    print ('Deleted: ' + x)
                    self.deletedlinks.append(x)
                    links.remove(x)
            i += 1

        links = list(set(links))

    def fixlinks(self, links=0):
        if links == 0:
            links = self.links

        self.fiximgur()
        self.fixerosh()
        self.fixgfycat()

    # def getimgur(self):
    #     if links == 0:
    #         links = self.links[:]

    #     imgurlinks = []

    #     for x in links:
    #         if 'imgur' in x:
    #             imgurlinks.append(x)
    #     return imgurlinks

    # def geteroshare(self,links=0):
    #     if links == 0:
    #         links = self.links[:]

    #     eroshlinks = []

    #     for x in links:
    #         if 'eroshare' in x:
    #             eroshlinks.append(x)
    #     return eroshlinks

    # def getgfycat(self,links=0):
    #     if links == 0:
    #         links = self.links[:]

    #     gfycatlinks = []

    #     for x in links:
    #         if 'gfycat' in x:
    #             gfycatlinks.append(x)
    #     return gfycatlinks

    # def fiximgur(self, links=0):
    #     if links == 0:
    #         links = self.links[:]
    #     return links
    def download(self, *args):
        for x in args:
            if 'imgur' in x:
                self.downloadlink(self.imgurlinks)
            elif 'erosh' in x:
                self.downloadlink(self.eroshlinks)
            elif 'gfycat' in x:
                self.downloadlink(self.gfycat)
            else:
                print('Usage: download(url) url = imgur or erosh or gfycat')

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

        for x in links:

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

                    print(' Downloading [%s/%s]: %s' % (links.index(x) + 1, len(links), x))
                    try:
                        wget.download(x, out='Reddit/- new/%s/%s' % (self.subreddit, filename))
                    except:
                        print(' ERROR - Skipping [%s/%s]: %s' % (links.index(x) + 1, len(links), x))
                else:
                    print(' Skipping [%s/%s]: %s' % (links.index(x) + 1, len(links), x))

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
                            self.eroshlinks.append([album_name, mp4list])
                        else:
                            self.links[self.links.index(x)] = mp4list[0]
                            self.eroshlinks.append(mp4list[0])

                    elif 'jpg' in source:
                        for y in soup.find_all('div', {'class':'blurred-bg'}):
                            imagelist.append('https://' + str(y).split('//')[1][:-10])
                        if len(imagelist) > 1:
                            album_name = x.split('/')[-1]
                            self.links[self.links.index(x)] = [album_name, imagelist]
                            self.eroshlinks.append([album_name, imagelist])
                        else:
                            self.links[self.links.index(x)] = imagelist[0]
                            self.eroshlinks.append(imagelist[0])

                    else:
                        self.links.remove(x)

                except:
                    print('remove:', x)
                    self.links.remove(x)

    # -------------------------------------------------- #
    def fixgfycat(self, links=0):
        '''
         This will fix gfycat links
        '''
        if links == 0:
            links = self.links[:]
            ret = True
        else:
            ret = False

        for x in links:
            if 'gfycat' in x and not any(y in x for y in ['mp4','gif','webm','gifv', 'giant']):
                try:
                    print('Processing:', x)
                    link = x.replace('gfycat.com/', 'gfycat.com/cajax/get/')
                    r = requests.get(link)
                    j = json.loads(r.text)
                    links[links.index(x)] = j['gfyItem']['mp4Url']
                    self.gfycatlinks.append(j['gfyItem']['mp4Url'])

                except:
                    print('remove:', x)
                    links.remove(links.index(x))
        
        if ret:
            self.links = links
        else:
            return links


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
                    self.imgurlinks.append(j['data']['link'])

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
                    self.imgurlinks.append([album_name, images])

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

if __name__ == '__main__':
    arnel = Reddit()
    arnel.fixlinks()