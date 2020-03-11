import re
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')
from nltk.stem import WordNetLemmatizer 
nltk.download('wordnet')
from nltk.corpus import stopwords
nltk.download('stopwords')

def normalize(text, is_query=False):
    text = text.lower() #to lower case
    # dealing with numbers (remmoving)
    text = re.sub(r'[0-9]', ' ', text) # removing
    # removing punctuations, accent marks and other diacritics
    # also removes dots from abbreviations 
    # allowed asterisk (0)
    # text = re.sub(r'[^\w\s\*]', '', text)
    if is_query:
        text = re.sub(r'[^\w\s\*]', '', text)
    else:
        text = re.sub(r'[^\w\s]', '', text)
    # remove unnecessery space symbols
    text = re.sub(r'[\s]+', ' ', text)
    return text

def tokenize(text):
    return word_tokenize(text)

def lemmatization(tokens):
    lemmatizer = WordNetLemmatizer() 
    return [lemmatizer.lemmatize(i) for i in tokens]

def remove_stop_word(tokens):
    stopWords = set(stopwords.words('english'))
    filtered_words = [token for token in tokens if token not in stopWords]
    return filtered_words

def preprocess(text):
    return (remove_stop_word(lemmatization(tokenize(normalize(text)))))