from forms import QueryForm
from flask import Flask, flash, render_template, request, redirect
from process_query import *
from crawler import Collection, Song
from indexes import Soundex, Inverted_index, Prefix_tree, create_prefix_trees, Search_engine
from threading import Thread
from time import sleep

corpus = Collection(from_file=True)
corpus_dict = dict(map(lambda x: (x.id, x), corpus.collection))
inv_ind = Inverted_index(corpus_dict)
pref_ind, rev_ind = create_prefix_trees(corpus.collection)
sound_ind = Soundex(corpus.collection)
aus = set()
to_rm = set()
en = Search_engine(corpus_dict, inv_ind, sound_ind, pref_ind, rev_ind)
app = Flask(__name__)
@app.route('/results')
def search_results(search):
    results = search_query(en.index, search.search.data, en.sound_ind, en.pref_ind, en.rev_ind, en.aux, en.to_rm)
    res = []
    for x in results:
        try:
            res.append(en.ind_to_doc[x])
        except:
            pass
    
    '''
    results = []
    results = ['1', '2']
    '''
    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('index.html', results=res, form=search)

@app.route('/', methods=['GET', 'POST'])
def index():
    search = QueryForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('index.html', results=None, form=search)

def background_update():
    while True:
        for i in range(5):
            new_docs = corpus.add_docs(5)
            for doc in new_docs:
                en.add_doc(doc)
            sleep(1)
        en.merge()
        print('merge')
        sleep(1)


if __name__ == '__main__':
    thr1 = Thread(target=background_update)
    thr1.start()
    app.secret_key = 'super secret key'
    app.run(debug=True, port=80)
