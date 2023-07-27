from __future__ import annotations

from abc import ABC
from abc import abstractmethod

import pandas as pd
from models import Article
from models import EmbeddedArticle
from models import Event
from sklearn.cluster import OPTICS
from utils import cluster_each_window
from utils import get_event_title
from utils import get_modal_date
from utils import partition_into_windows
from utils import remove_largest_cluster_of_each_window


class AbstractPipeline(ABC):
    """Abstract pipeline to generate events from articles"""

    @abstractmethod
    def generate_events(self, articles: list[EmbeddedArticle]) -> list[Event]:
        pass


class SlidingWindowOpticsPipeline(AbstractPipeline):
    def _parse_into_events(self, clusters_for_each_window: list[list[pd.DataFrame]]) -> list[Event]:
        events = []
        for window in clusters_for_each_window:
            for cluster in window:
                article_dicts = cluster.drop(columns=["embeddings"]).to_dict("records")
                articles = [Article(**article_dict) for article_dict in article_dicts]
                event = Event(
                    name=get_event_title(cluster),
                    date=get_modal_date(cluster).isoformat(),
                    articles=articles,
                )
                events.append(event)
        return events

    def generate_events(self, articles: list[EmbeddedArticle]) -> list[Event]:
        article_dicts = [dict(article) for article in articles]
        df = pd.DataFrame.from_records(article_dicts)

        if df.empty:
            return []

        df.date_published = pd.to_datetime(df.date_published)

        sliding_windows = partition_into_windows(df, 1, 3)
        sliding_windows = [window for window in sliding_windows if len(window) > 2]

        min_samples = 2 if len(df) < 200 else 3
        optics = OPTICS(min_samples=min_samples, xi=0.05)
        clusters_for_each_window = cluster_each_window(optics, sliding_windows)

        # Largest cluster is usually filled with articles that don't
        # constitute an event, i.e. a "junk" cluster.
        clusters_for_each_window = remove_largest_cluster_of_each_window(clusters_for_each_window)

        events = self._parse_into_events(clusters_for_each_window)
        return sorted(events, key=lambda event: event.date, reverse=True)
