
import pandas as pd
from sklearn.cluster import OPTICS
from typing import List

from backend.models import Article
from ml.data_processing import partition_data_into_windows, process_text_columns
from ml.models import cluster_each_window, embed_articles
from ml.utils import parse_into_events, remove_largest_cluster_of_each_window


def sliding_window_optics_pipeline(articles: List[Article]):
    df = pd.DataFrame.from_records(articles)

    if df.empty:
        return []
  
    df.date_published = pd.to_datetime(df.date_published)

    df['embeddings'] = embed_articles(df)
    
    sliding_windows = partition_data_into_windows(df, 1, 3)
    
    if len(df) < 200:
        min_samples = 2
    else:
        min_samples = 3

    sliding_windows = [window for window in sliding_windows if len(window) >= min_samples]
    
    optics = OPTICS(min_samples=min_samples, xi=0.05)
    clusters_for_each_window = cluster_each_window(optics, sliding_windows, keep_embeddings=True)
    
    # Largest cluster is usually (>99% of the time) filled with articles 
    # that don't constitute an event, i.e. a "junk" cluster.
    clusters_for_each_window = remove_largest_cluster_of_each_window(clusters_for_each_window)
    
    return parse_into_events(clusters_for_each_window)
