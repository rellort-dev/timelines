
import pandas as pd
from abc import ABC, abstractmethod
from sklearn.cluster import OPTICS

from models import EmbeddedArticle, Event
from utils import (
    get_event_title,
    get_modal_date,
    remove_largest_cluster_of_each_window,
    partition_into_windows,
    cluster_each_window,
)


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
                event = {
                    'name': get_event_title(cluster),
                    'date': get_modal_date(cluster).isoformat(),
                    'articles': cluster.drop(columns=['embeddings']).to_dict('records')
                }
                events.append(event)
        return events

    def generate_events(self, articles: list[EmbeddedArticle]) -> list[Event]:
        article_dicts = [dict(article) for article in articles]
        df = pd.DataFrame.from_records(article_dicts)

        if df.empty:
            return []

        df.date_published = pd.to_datetime(df.date_published)

        sliding_windows = partition_into_windows(df, 1, 3)

        min_samples = 2 if len(df) < 200 else 3
        optics = OPTICS(min_samples=min_samples, xi=0.05)
        clusters_for_each_window = cluster_each_window(optics, sliding_windows)

        # Largest cluster is usually filled with articles that don't
        # constitute an event, i.e. a "junk" cluster.
        clusters_for_each_window = remove_largest_cluster_of_each_window(clusters_for_each_window)

        events = self._parse_into_events(clusters_for_each_window)
        return sorted(events, key=lambda event: event['date'], reverse=True)
