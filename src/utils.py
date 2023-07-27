from __future__ import annotations

import copy
import json
import os
from datetime import date
from datetime import timedelta
from pathlib import Path

import numpy as np
from models import Timeline
from pandas import DataFrame
from sklearn.base import BaseEstimator
from sklearn.metrics import pairwise_distances_argmin_min


def daterange(start: date, end: date, step: timedelta = timedelta(days=1)):
    for n in range(0, int((end - start).days), step.days):
        yield start + timedelta(n)


def partition_into_windows(
    articles_df: DataFrame,
    window_delta: int = 0,
    step: int = 1,
) -> list[DataFrame]:
    """
    Partitions the dataframe into windows of articles
    published within [day - window_delta, day + window_delta]

    Examples:
        Parameters           Days contained in each window
    window_delta=0, step=1 --> [4-4, 5-5, 6-6, ...]
    window_delta=1, step=1 --> [3-5, 4-6, 5-7, ...]
    window_delta=2, step=1 --> [2-6, 3-7, 4-8, ...]
    window_delta=0, step=2 --> [4-4, 6-6, 8-8, ...]
    """

    windows = []

    window_size = timedelta(days=window_delta)
    start_date = articles_df.date_published.dt.date.min()
    end_date = articles_df.date_published.dt.date.max()

    for d in daterange(
        start_date + window_size,
        end_date - window_size + timedelta(days=1),
        timedelta(days=step),
    ):
        lower_bound = d - window_size
        upper_bound = d + window_size
        is_within_window = (lower_bound <= articles_df.date_published.dt.date) & (
            articles_df.date_published.dt.date <= upper_bound
        )
        data_within_window = articles_df[is_within_window]
        windows.append(data_within_window)

    return windows


def partition_into_clusters(
    data: DataFrame,
    fitted_clustering_model: BaseEstimator,
) -> list[DataFrame]:
    """Splits the DataFrame based on the labels assigned by the fitted model"""

    unique_labels = np.unique(fitted_clustering_model.labels_)
    data = [data[fitted_clustering_model.labels_ == label] for label in unique_labels]
    return data


def cluster_each_window(
    model: BaseEstimator,
    sliding_windows: list[DataFrame],
) -> list[list[DataFrame]]:
    """Clusters each window using the provided model"""

    clusters_for_each_window = []
    for window_df in sliding_windows:
        x = np.stack(window_df.embeddings)
        model = model.fit(x)
        clusters = partition_into_clusters(window_df, model)
        clusters_for_each_window.append(clusters)
    return clusters_for_each_window


def remove_largest_cluster_of_each_window(
    clusters_for_each_window: list[list[DataFrame]],
) -> list[list[DataFrame]]:
    """
    Removes the largest cluster within each window. The largest cluster is usually
    filled with articles that don't constitute an event, i.e. a "junk" cluster.

    Args:
        clusters_for_each_window: clusters_for_each_window[w][c] is the
            DataFrame corresponding to the c-th cluster of the w-th window
    """
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


def get_event_title(event: DataFrame) -> str:
    """Returns the title closest to the mean embedding of the event"""
    embeddings = [embedding for embedding in event.embeddings]
    mean_embedding = np.array([np.mean(embeddings, axis=0)])
    index = pairwise_distances_argmin_min(mean_embedding, embeddings)[0][0]
    return event.title.iloc[index]


def get_modal_date(event: DataFrame) -> date:
    """Returns the modal date of articles in that event"""
    dates = event.date_published.dt.date
    return dates.mode()[0]


def store_locally(timeline: Timeline, query: str) -> None:
    results_dir = Path("../.results")
    results_dir.mkdir(parents=True, exist_ok=True)

    filename = query.replace(" ", "_") + ".json"
    results_file = os.path.join(results_dir, filename)
    with open(results_file, "w") as f:
        json.dump(timeline.model_dump(mode="json"), f, indent=4)


def build_key_on_query(query: str) -> str:
    return f"timeline-{query}"
