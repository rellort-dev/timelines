import numpy as np
from .utils import partition_into_clusters
import sentence_transformers
import torch
import gc

device = "cuda" if torch.cuda.is_available() else "cpu"
sent_transformer = sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2', device=device)
sent_transformer.max_seq_length = 512
def embed_articles(df):
    '''
    Generates article embeddings `embeddings` column.
    '''
    title_embeddings = sent_transformer.encode(list(df.title))
    body_embeddings = sent_transformer.encode(list(df.body))
    embeddings = (0.5 * title_embeddings) + (0.5 * body_embeddings)

    torch.cuda.empty_cache()
    gc.collect()

    return list(embeddings)


def cluster_each_window(model, sliding_windows, keep_embeddings=False):
    '''
    Given a model and a list of DataFrames, where sliding_windows[w] is a DataFrame of articles,  
    Returns a list of list of DataFrames, where clusters_for_each_window[w][c]
    is the DataFrame corresponding to the c-th cluster for the w-th window.
    '''

    clusters_for_each_window = []
    for window in sliding_windows:
        x = np.stack(window.embeddings)
        model = model.fit(x)

        if not keep_embeddings:
            window = window.drop(columns=['embeddings'])

        clusters = partition_into_clusters(window, model)
        clusters_for_each_window.append(clusters)
    return clusters_for_each_window
