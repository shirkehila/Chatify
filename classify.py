import gensim
from gensim.test.utils import datapath, get_tmpfile
from gensim.corpora.dictionary import Dictionary
from gensim.corpora import Dictionary
from pprint import pprint as pp
import nltk
from nltk.corpus import wordnet as wn
from spacy.lang.en import English

model_path = 'model.gensim'
dict_name = 'dictionary'
en_stop = set(nltk.corpus.stopwords.words('english'))
parser = English()


def tokenize(text):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens


def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


def prepare_text_for_lda(text):
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens]
    return tokens



class Classifier:
    def __init__(self, path, dict_name):
        self._model = gensim.models.ldamodel.LdaModel.load(datapath(path))
        self._dictionary = Dictionary.load_from_text(get_tmpfile(dict_name))

    def classify(self,text):
        tokens = prepare_text_for_lda(text)
        d2b = self.doc2bow_tokens(tokens)
        return self._model.get_document_topics(d2b)

    def get_topics(self,num_words):
        return self._model.print_topics(num_words=num_words)

    def doc2bow_tokens(self,tokens):
        return self._dictionary.doc2bow(tokens)