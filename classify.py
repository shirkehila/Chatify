import gensim
from gensim.test.utils import datapath, get_tmpfile
from gensim.corpora import Dictionary
import nltk
from nltk.corpus import wordnet as wn
from spacy.lang.en import English
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer


class Classifier:
    def __init__(self, path, dict_name):
        self._model = gensim.models.ldamodel.LdaModel.load(datapath(path))
        self._dictionary = Dictionary.load_from_text(get_tmpfile(dict_name))
        self._en_stop = set(nltk.corpus.stopwords.words('english'))
        self._parser = English()
        self._lemmatizer = WordNetLemmatizer()

    def tokenize(self,text):
        lda_tokens = []
        tokens = self._parser(text)
        for token in tokens:
            if token.orth_.isspace():
                continue
            elif token.like_url:
                continue
            elif token.orth_.startswith('@'):
                continue
            else:
                lda_tokens.append(token.lower_)
        return lda_tokens

    def get_wordnet_pos(self, word):
        """Map POS tag to first character lemmatize() accepts"""
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}

        return tag_dict.get(tag, wordnet.NOUN)

    def lemmatize(self, tokens):
        return [self._lemmatizer.lemmatize(w, self.get_wordnet_pos(w)) for w in tokens]

    def prepare_text_for_lda(self,text):
        tokens = self.tokenize(text)
        tokens = [token for token in tokens if len(token) > 4]
        tokens = [token for token in tokens if token not in self._en_stop]
        tokens = self.lemmatize(tokens)
        return tokens

    def classify(self,text):
        tokens = self.prepare_text_for_lda(text)
        d2b = self.doc2bow_tokens(tokens)
        return self._model.get_document_topics(d2b)

    def get_topics(self,num_words):
        return self._model.print_topics(num_words=num_words)

    def doc2bow_tokens(self,tokens):
        return self._dictionary.doc2bow(tokens)

    def class_and_words(self, text):
        """gets text and returns:
        1.percentage for classification
        2.topic with highest probabilty
        3.top words for the topic"""
        # classification with percentage
        perc = self.classify(text)
        data_d = {x: y for x, y in perc}
        data_d = sorted(data_d, key=data_d.get, reverse=True)
        topic = data_d[0]
        # top words for highest probabilty
        words = self.get_topics(10)[topic]
        t_words = words[1].split('"')
        t_words = [w for w in t_words if w.isalpha()]
        t_words = ", ".join(t_words)
        t_words = t_words
        return perc, topic, t_words
