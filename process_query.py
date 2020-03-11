from preprocessing import *

def preprocess_query(query, sound_ind, pref_ind, reverse_ind):
    res_query = []
    tokens = tokenize(normalize(query, is_query=True))
    for t in tokens:
        # (2.1) check is token is in a corpus
        if pref_ind.is_token_in(t):
            res_query.append([t])
            continue
        # (2.2) check if it is wildcard
        if '*' in t:
            if len(t.split('*')) > 3:
                print(f'too much * in the word {t}, it is not allowed')
                return False
            t_s  = t.split('*')
            l1 = pref_ind.find_all(t_s[0])
            #bug smw here !!!
            l2 = pref_ind.find_all(t_s[-1][:: -1])
            # case: find any token 
            if l1 == True and l2 == True:
                continue
            if l1 == True:
                res = l2
                #res_query.append(l2)
            elif l2 == True:
                res = l1
                #res_query.append(l1)
            else:
                res = list(set(l1).intersection(set(l2)))
                #res_query.append(list(set(l1).intersection(set(l2))))
            pattern = re.compile(re.sub(r'\*', '.*', t))
            tmp = []
            for i in res:
                m = pattern.match(i)
                if m and len(m[0]) == len(i):
                    tmp.append(m[0])
            res_query.append(tmp)
            continue
        # (2.3)
        sound = sound_ind.soundex(t)
        similar = list(sound_ind.inverted_index[sound])
        distances = list(map(lambda x: sound_ind.count_levenhstein(x, t), similar))
        min_dist = min(distances)
        res_query.append([similar[i] for i in range(len(distances)) if distances[i] == min_dist])
    # (2.4) clean: remove all stop words and lemmatize
    cleaned = []
    for l in res_query:
        cl = remove_stop_word(lemmatization(l))
        if len(cl) != 0:
            cleaned.append(cl)
    return cleaned

def find_docs_with_word(t, index, aux=set(), to_rm=set()):
    regular = index.get_list(t)
    no_old = regular.difference(to_rm)
    return no_old.union(aux)

def make_or(index, terms, aux=set(), to_rm=set()):
    rel_docs = set()
    for t in terms:
        rel_docs = rel_docs.union(find_docs_with_word(t, index, aux, to_rm))
    return rel_docs

def search_query(index, query, sound_ind, prer_ind, reverse_ind):
    query = preprocess_query(query, sound_ind, prer_ind, reverse_ind)
    rel_docs = set()
    flag = True
    for or_statements in query:
        or_res = make_or(index, or_statements)
        if flag:
            flag = False
            rel_docs.update(or_res)
        else:
            rel_docs = rel_docs.intersection(or_res)
    return rel_docs