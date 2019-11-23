import pandas as pd
import syllabels_en
import pickle
from textblob import TextBlob

def _get_n_words(text):
    blob = TextBlob(text)
    return len(blob.ngrams(n=1))

def _get_n_chars(text):
    chars = text.replace(' ', '').replace('.', '').replace('?', '')
    chars = chars.replace("'", '').replace('"', "")
    return len(chars)

def _get_n_sentences(text):
    blob = TextBlob(text)
    return len(blob.sentences)

def _get_n_syllabels(words):
    if words is None:
      words = []

    return sum([syllabels_en.count(word) for word in words])

def ARI(row):
    """
    1: kindegarten
    14: college
    """
    text = row['caption']
    sentences = _get_n_sentences(text)
    words = _get_n_words(text)
    characters = _get_n_chars(text)
    if words == 0:
        return 0
    return 4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43

def flesch(row):
    """
    30-0: college level
    100-90: 5th grade
    """
    text = row['caption']
    sentences = _get_n_sentences(text)
    words = _get_n_words(text)
    characters = _get_n_chars(text)
    syllabels = _get_n_syllabels(text)

    if words == 0:
        return 100

    return 206.835 - 1.015 * (words / sentences) - 84.6 * (syllabels / words)



def caption_stats(row):
    """ blob.sentiment trained on pos/neg movie reviews """
    caption = row['caption']
    blob = TextBlob(caption)

    proper_nouns = ['NNP' in tag for _, tag in blob.tags]
    indef_articles = [word.lower() in ['a', 'an', 'some']
                      for word in caption.split()]
    pos_words = {'pronouns': ['you', 'i', 'it', 'my', 'we', 'me', 'your', 'their'],
                 'question_words': ['how', 'what'],
                 'negation_words': ["don't", 'no', 'not', "ain't", "can't"],
                 'aux_verbs': ['do', 'should', 'need', 'can', 'think'],
                 'indef_articles': ['a', 'an']}

    n_pos_words = {key: sum([word.lower() in pos_words[key]
                             for word in caption.split()])
                   for key in pos_words}

    return {'sentiment': blob.sentiment.polarity,
            'proper_nouns': sum(proper_nouns),
            'n_words': _get_n_words(caption),
            'n_sentences': _get_n_sentences(caption),
            **n_pos_words}

if __name__ == "__main__":
    df = pd.read_csv('data/summary.csv')

    df['readability_ARI'] = df.apply(ARI, axis=1)
    df['readability_Flesch'] = df.apply(flesch, axis=1)
    stats = pd.DataFrame(list(df.apply(caption_stats, axis=1)))
    df = pd.concat([df, stats], axis=1)
