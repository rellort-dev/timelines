
import pandas as pd
from sklearn.cluster import OPTICS
from ml.data_processing import partition_data_into_windows, process_text_columns
from ml.models import cluster_each_window, embed_text_column
from ml.utils import parse_into_events, remove_largest_cluster_of_each_window
from config import config


def sliding_window_optics_pipeline(df):
    '''
    Processing: Lowercase all, only keep alphanumerical, combine all text columns.
    Embeddings: Spacy 
    Clustering algorithm: Sliding-window OPTICS 
    '''
  
    # Data processing
    df = process_text_columns(df)
    df.date_published = pd.to_datetime(df.date_published)
    df.to_csv(f'{config.DATA_DIR}/china_lockdown.csv', index=False)

    # Embedding text columns
    df_with_embeddings = embed_text_column(df)
    
    # Sliding window partitioning 
    sliding_windows = partition_data_into_windows(df_with_embeddings, 1, 3)
    
    # Selecting hyperparameters
    if len(df) < 200:
        min_samples = 2
    else:
        min_samples = 3

    # Remove windows with less than min_samples samples
    sliding_windows = [window for window in sliding_windows if len(window) >= min_samples]
    
    # Clustering
    optics = OPTICS(min_samples=min_samples, xi=0.05)
    clusters_for_each_window = cluster_each_window(optics, sliding_windows, keep_embeddings=True)
    
    # Largest cluster is usually (>99% of the time) filled with unimportant events 
    clusters_for_each_window = remove_largest_cluster_of_each_window(clusters_for_each_window)
    
    return parse_into_events(clusters_for_each_window)