
import copy
from datetime import timedelta
import numpy as np
from sklearn.metrics import pairwise_distances_argmin_min


def daterange(start_date, end_date, step=timedelta(days=1)):
    for n in range(0, int((end_date - start_date).days), step.days):
        yield start_date + timedelta(n)


def partition_into_clusters(data, fitted_model):
    '''
    Given a DataFrame and a model fitted on that DataFrame, 
    returns a list of DataFrames, where each DataFrame contains 
    data of the same cluster, as labelled by the fitted_model.
    '''

    labels = np.unique(fitted_model.labels_)
    data = [data[fitted_model.labels_ == label] for label in labels]
    return data


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


def get_event_title(event):
    '''
    Given an event (a DataFrame of articles),
    Returns the title of that event.
    '''
    embeddings = [embedding for embedding in event.embeddings]
    mean_embedding = np.array([np.mean(embeddings, axis=0)])
    index = pairwise_distances_argmin_min(mean_embedding, embeddings)[0][0]
    return event.title.iloc[index]


def get_modal_date(event):
    '''
    Given an event (a DataFrame of articles),
    Returns the modal date of articles in that event.
    '''
    dates = event.date_published.dt.date
    return dates.mode()[0]


def to_article_dicts(event):
    '''
    Given a DataFrame representing a cluster of articles,
    Returns a list of dictionaries, where each dictionary is an article.
    '''
    event = event.drop(columns=['body', 'embeddings'])
    return event.to_dict('records')


def parse_into_events(clusters_for_each_window):
    '''
    Given a list of list of DataFrames, where clusters_for_each_window[w][c]
    is the DataFrame corresponding to the c-th cluster for the w-th window,
    Returns a list of events sorted by date, where each event is a dictionary:
    {
        'name': string
        'date': date
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
            event = {
                'name': get_event_title(cluster),
                'date': get_modal_date(cluster).isoformat(), 
                'articles': to_article_dicts(cluster)
            }
            events.append(event)
    return sorted(events, key=lambda event: event['date'], reverse=True)
