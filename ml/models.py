import numpy as np
import spacy
from sklearn import clone
from .utils import partition_articles_into_clusters

nlp = spacy.load('en_core_web_lg', exclude=['ner', 'tagger', 'parser', 'lemmatizer', 'textcat', 'attribute_ruler', 'senter'])

def embed_text_column(df):
    '''
    Embeds the `text` column of a DataFrame into an `embeddings` column.
    '''

    docs = list(nlp.pipe(df.text))
    embeddings = [doc.vector for doc in docs]
    df_with_embeddings = df.copy()
    df_with_embeddings['embeddings'] = embeddings
    return df_with_embeddings


def cluster_each_window(model, sliding_windows, keep_raw_text=False, keep_embeddings=False):
    '''
    Given a model and a list of DataFrames, where sliding_windows[w] is a DataFrame of articles,  
    Returns a list of list of DataFrames, where clusters_for_each_window[w][c]
    is the DataFrame corresponding to the c-th cluster for the w-th window.
    '''

    clusters_for_each_window = []
    for window in sliding_windows:
        x = np.stack(window.embeddings)
        model = clone(model).fit(x)  # Clone to reset parameters before fitting again
        
        if not keep_embeddings:
            window = window.drop(columns=['embeddings'])
        if not keep_raw_text:
            window = window.drop(columns=['text'])

        clusters = partition_articles_into_clusters(window, model)
        clusters_for_each_window.append(clusters)
    return clusters_for_each_window
