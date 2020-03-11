from forms import QueryForm
from flask import Flask, flash, render_template, request, redirect
from process_query import *
from crawler import Collection, Song
from indexes import Soundex, Inverted_index, Prefix_tree, create_prefix_trees

corpus = Collection(from_file=True)
corpus_dict = dict(map(lambda x: (x.id, x), corpus.collection))
inv_ind = Inverted_index(corpus_dict)
pref_ind, rev_ind = create_prefix_trees(corpus.collection)
sound_ind = Soundex(corpus.collection)

app = Flask(__name__)
@app.route('/results')
def search_results(search):
    results = search_query(inv_ind, search.search.data, sound_ind, pref_ind, rev_ind)
    results = [corpus_dict[x] for x in results]
    '''
    results = []
    results = ['1', '2']
    '''
    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('index.html', results=results, form=search)

@app.route('/', methods=['GET', 'POST'])
def index():
    search = QueryForm(request.form)
    if request.method == 'POST':
        print('kek')
        return search_results(search)
    return render_template('index.html', results=None, form=search)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True, port=80)