import shutil
from preprocessing import *
from pathlib import Path
import pickle
import re
import numpy as np

# main index
class Inverted_index:

    def __init__(self, corpus_dict, batch_size=50):
        self.path_to_ind = Path('data/index')
        self.rm_ind()
        counter = 0
        inverted_index = {}
        for id_, doc in corpus_dict.items():
            clean = lemmatization(tokenize(normalize(doc.text)))
            for word in clean:
                if not (word in inverted_index):
                    inverted_index[word] = set()
                inverted_index[word].add(id_)
            if counter == batch_size:
                counter = 0
                self.serialize(inverted_index)
                inverted_index = {}
            else:
                counter += 1
        if counter > 0:
            self.serialize(inverted_index)
    
    def serialize(self, index, to_rm=set()):
        for w, docs in index.items():
            old = set()
            try:
                old = pickle.load((self.path_to_ind / w).open('rb'))
            except:
                pass
            pickle.dump(old.union(docs).difference(to_rm), (self.path_to_ind / w).open('wb'))
        pass
            
    def merge(self, aux, to_rm):
        # TODO test merge
        self.serialize(aux, to_rm=to_rm)
    
    def get_list(self, w):
        try:
            return pickle.load((self.path_to_ind / w).open('rb'))
        except:
            return set()
        
    def rm_ind(self):
        shutil.rmtree(self.path_to_ind)
        self.path_to_ind.mkdir()
#reg_ind = Inverted_index(corpus_dict)        

# Prefix trees
class Node:
    
    def __init__(self, ch, parent):
        self.char = ch
        self.children = {}
        self.is_token = False
        self.parent = parent
      
    
class Prefix_tree:

    def __init__(self):
        self.root = Node('', None)
    
    def add(self, token):
        cur_root = self.root
        for ch in token:
            try:
                if not (ch in cur_root.children):
                    cur_root.children[ch] = Node(ch, cur_root)
            except:
                print(self.root == cur_root)
            cur_root = cur_root.children[ch]
        # in such tree not only leaves can be possible tokens, e.g. cat and caterpillar
        cur_root.is_token = True
        
    def find(self, token):
        cur_root = self.root
        for ch in token:
            if not(ch in cur_root.children):
                return None
            cur_root = cur_root.children[ch]
        return cur_root
    
    def is_token_in(self, token):
        cur_root = self.find(token)
        if cur_root == None:
            return False
        # true iff the token in the tree and it's a token, not just prefix
        return cur_root.is_token
    
    def find_all(self, token):
        to_find = token.split('*')[0]
        if to_find == '':
            return True
        cur_root = self.find(to_find)
        if cur_root == None:
            return []
        return self.traverse(cur_root, to_find)
    
    def traverse(self, node, string):
        tokens = []
        if node.is_token:
            tokens.append(string)
        for k, val in node.children.items():
            tokens.extend(self.traverse(val, string + k))
        return tokens
    
    def rm(self, token):
        #TODO is it required??
        node = self.find(token)
        if node == None or not node.is_token:
            return
        if len(node.children) == 0:
            del node.parent.children[token[-1]]
        else:
            node.is_token = False
            
        
def create_prefix_trees(collection):
    direct_prefix = Prefix_tree()
    reverse_prefix = Prefix_tree()
    for doc in collection:
        clean = remove_stop_word(tokenize(normalize(doc.text)))
        for word in clean:
            direct_prefix.add(word)
            reverse_prefix.add(word[::-1])
    return direct_prefix, reverse_prefix
#pref_ind, rev_ind = create_prefix_trees(corpus.collection)
  

# Soundex
class Soundex:
    
    def __init__(self, collection):
        self.inverted_index = {}
        for doc in collection:
            clean = tokenize(normalize(doc.text))
            for word in clean:
                try:
                    sound = self.soundex(word)
                except:
                    continue
                if not (sound in self.inverted_index):
                    self.inverted_index[sound] = set()
                self.inverted_index[sound].add(word)
                
    def soundex(self, term):
        mapper = {'a': 0, 'e': 0, 'i': 0, 'o': 0, 'u': 0, 'h': 0, 'w': 0, 'y': 0,\
                  'b': 1, 'f': 1, 'p': 1, 'v': 1,\
                  'c': 2, 'g': 2, 'j': 2, 'k': 2, 'q': 2, 's': 2, 'x':2 , 'z':2,\
                  'd': 3, 't': 3,\
                  'l': 4,\
                  'm': 5, 'n': 5,\
                  'r': 6
                 }
        # convert all excluding 1st to digits
        tmp  = ''.join(list(map(lambda x: str(mapper[x]), term.lower())))
        # sequences to one digit 
        tmp = re.sub(r'(.)\1{1,}', r'\1', tmp)
        # remove zeroes
        tmp = re.sub(r'0', '', tmp)
        # check if the first letter werer skipped (0) and pad with '0'
        tmp = term[0].upper() + (tmp[1:] if mapper[term[0].lower()] != 0 else tmp) + '0' * 4
        return tmp[:4]

    def add(self, t):
        sound = self.soundex(t)
        if not(sound in self.inverted_index):
            self.inverted_index[sound] = set()
        self.inverted_index[sound].add(t)

    def count_levenhstein(self, t1, t2):
        d = np.zeros((len(t1) + 1, len(t2) + 1))
        for i in range(len(t1) + 1):
            for j in range(len(t2) + 1):
                if i == 0:
                    d[i, j] = j
                    continue
                if j == 0:
                    d[i, j] = i
                    continue
                d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1,\
                              d[i - 1, j - 1] + (0 if t1[i - 1] == t2[j - 1] else 1))
        return d[-1, -1] 

class Search_engine:
    def __init__(self, ind_to_doc, inv_index, sound_ind, pref_ind, rev_ind):
        self.index = inv_index
        self.sound_ind = sound_ind
        self.pref_ind = pref_ind
        self.rev_ind = rev_ind
        self.aux = {}
        self.to_rm = set()
        self.ind_to_doc = ind_to_doc
        
    def add_doc(self, doc):
        self.ind_to_doc[doc.id] = doc
        clean = lemmatization(tokenize(normalize(doc.text)))
        for word in clean:
            if not (word in self.aux):
                self.aux[word] = set()
            self.aux[word].add(doc.id)
            self.pref_ind.add(word[::-1])            
            self.rev_ind.add(word)
            self.sound_ind.add(word)

    def rm_doc(self, doc):
        self.to_rm = self.to_rm.add(doc.id)
        pass
    
    def merge(self):
        self.index.merge(self.aux, self.to_rm)
        # TODO rm from in memory inds
        aux = {}
        to_rm = set()
        pass

