from time import sleep
import requests
import re
from bs4 import BeautifulSoup
import pickle
from pathlib import Path

class Song:
    @property
    def text(self):
        '''
        text is stored localy
        '''
        return open(self.path, 'r').read()
    @property
    def path(self):
        '''
        path to the song
        '''
        return(self.path_to_par / 'songs' / self.id)
    
    def __init__(self, title, artist, text, _id, path):
        self.path_to_par = Path(path)
        self.title = title
        self.artist = artist
        self.id = _id
        try:
            self.path.open('w').write(text)
        except Exception as e:
            return None


# TODO add dates so that can be removed
# TODO dynamic crawling (aux)

class Collection:
    
    def __init__(self, path_to_storage = 'data/', from_file=False, init_number=200):
        self.path_to_storage = Path(path_to_storage)
        self.songs_ser_path = self.path_to_storage / 'songs_keaper'
        self.visited_ser_path = self.path_to_storage / 'visited'        
        if from_file:
            try:
                self.deserialize()
            except Exception as e:
                print(f'Exception: {e}')
        else:
            self.visited = set()
            self.collection = []
            (self.path_to_storage/'songs').mkdir()
            self.get_collection(init_number)
                
    def download(self, url):
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp
        return None

    def parse_page(self, page, url):
        '''
        :param page: content of the page
        :param url: url of the page
        parse page with lyrics, gets authors, title and text and load into memory 
        return 
        '''
        soup = BeautifulSoup(page, 'html.parser')
        try:
            title = soup.find(id='lyric-title-text').text #title
            #list af all authors
            group = soup.findAll('hgroup', {'dir': 'ltr'})[0]
            names = group.find_all("h3", {'class':'lyric-artist'})[0]
            a_s = names.find_all('a')
            authors = []
            for a in a_s:
                if re.match(f'artist/.+', a['href']):
                    authors.append(a.text)
            # song text
            text = soup.find(id='lyric-body-text').text
        except:
            print(f'Skipping page with url: {url}')
            return None
        return Song(title, authors, text, url.split('/')[-1], self.path_to_storage)
    
    def get_collection(self, count):
        '''
        :param count: number of docs to be in initial collection
        :return collection: array of Songs
        Create an initial collection to of size given size
        '''
        root = 'https://www.lyrics.com/'
        counter = 0
        while counter < count:
            # there are btn in the page, that allows to find random lyrics
            resp = self.download(root + 'random.php')
            if resp == None:
                continue
            if resp.url in self.visited:
                print(f'Already self.visited url{resp.url}')
                continue
            song = self.parse_page(resp.content, resp.url)
            if song == None:
                continue
            if song == False:
                continue
            self.collection.append(song)
            self.visited.add(resp.url)
            counter += 1
        self.serialize()

    def serialize(self):
        '''
        Saves collection as a file
        '''
        with self.songs_ser_path.open('wb') as f:
            pickle.dump(self.collection, f)
        with self.visited_ser_path.open( 'wb') as f:
            pickle.dump(self.visited, f)
    
    def deserialize(self):
        '''
        Load from local storage
        '''
        self.collection = pickle.load(self.songs_ser_path.open('rb'))
        self.visited = pickle.load(self.visited_ser_path.open( 'rb'))
        
    def add_docs(self, n):
        self.get_collection(n)
        return self.collection[-n:]
        
    def rm_doc(self):
        # TODO think about condition to rm
        pass
    

def crawling():
    collection = Collection(from_file=True)
    while True:
        collection.add(20)
        sleep(30)
