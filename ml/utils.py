import copy
from datetime import timedelta
import numpy as np
from sklearn.metrics import pairwise_distances_argmin_min

def daterange(start_date, end_date, skip_delta=timedelta(days=1)):
    for n in range(0, int((end_date - start_date).days), skip_delta.days):
        yield start_date + timedelta(n)

def partition_articles_into_clusters(articles, fitted_model):
    '''
    Given a DataFrame and a model fitted on that DataFrame, 
    returns a list of DataFrames, where each DataFrame contains 
    articles of the same cluster, as labelled by the fitted_model.
    '''

    labels = np.unique(fitted_model.labels_)
    articles = [articles[fitted_model.labels_ == label] for label in labels]
    return articles

def remove_largest_cluster_of_each_window(clusters_for_each_window):
    '''
    Given a list of list of DataFrames, where clusters_for_each_window[w][c]
    is the DataFrame corresponding to the c-th cluster for the w-th window,
    remove the largest cluster from each window.
    '''
    
    # Have to define custom helper function because remove(max(...)) raises
    # ValueError: Can only compare df with same index
    def remove_largest_df_in_list(dfs):
        largest_df_idx = 0
        for i in range(len(dfs)):
            if len(dfs[i]) > len(dfs[largest_df_idx]):
                largest_df_idx = i
        del dfs[largest_df_idx]
        
    clusters_for_each_window = copy.deepcopy(clusters_for_each_window)
    for clusters_for_window in clusters_for_each_window:
        remove_largest_df_in_list(clusters_for_window)
    return clusters_for_each_window

def get_cluster_title(cluster):
    '''
    Given a DataFrame representing a cluster of articles (i.e. an event), 
    Returns the title of that cluster (i.e. the title of the event).
    '''
    
    embeddings = [embedding for embedding in cluster.embeddings]
    mean_embedding = np.array([np.mean(embeddings, axis=0)])
    index = pairwise_distances_argmin_min(mean_embedding, embeddings)[0][0]
    return cluster.title.iloc[index]

def get_modal_date(cluster):
    '''
    Given a DataFrame representing a cluster of articles, 
    Returns the modal date of articles in that cluster.
    '''
    dates = cluster.date_published.dt.date
    return dates.mode()[0]

def get_cluster_articles_as_dicts(cluster):
    '''
    Given a DataFrame representing a cluster of articles, 
    Returns a list of dictionaries, where each dictionary is an article.
    '''
    cluster = cluster.drop(columns=['body','embeddings'])  # Include all columns except body and embeddings
    return cluster.to_dict('records')

def parse_into_events(clusters_for_each_window):
    '''
    Given a list of list of DataFrames, where clusters_for_each_window[w][c]
    is the DataFrame corresponding to the c-th cluster for the w-th window,
    Returns a list of events sorted by date, where each event is a dictionary:
    {
        'event_name': string
        'event_date': date
        'articles': [
            {
                'title': string
                'date_published': date
                'url': string
                'thumbnail_url': string
            }, 
        ]
    }
    '''
    
    events = []
    for window in clusters_for_each_window:
        for cluster in window:
            events.append({
                'event_name': get_cluster_title(cluster),
                'event_date': get_modal_date(cluster), 
                'articles': get_cluster_articles_as_dicts(cluster)
            })
    return sorted(events, key=lambda event : event['event_date'])
