
from abc import ABC, abstractmethod
from datetime import date, datetime
from meilisearch import Client

from models import EmbeddedArticle, Event
import config


class AbstractNewsClient(ABC):
    """Abstract client to fetch embedded news articles"""

    @abstractmethod
    def fetch_news(self, query: str, start: datetime, end: datetime) -> list[EmbeddedArticle]:
        pass


class MeilisearchNewsClient(AbstractNewsClient):

    def __init__(
        self,
        meilisearch_url: str,
        meilisearch_key: str,
        index_name: str
    ) -> None:
        self.meilisearch_client = Client(meilisearch_url, meilisearch_key)
        self.index = self.meilisearch_client.index(index_name)

    def fetch_news(self, query: str, before: datetime, after: datetime) -> list[EmbeddedArticle]:
        published_time_filter = f"publishedTime >= {after.timestamp()} AND publishedTime < {before.timestamp()}"
        source_filter = f"source NOT IN [{', '.join(config.DISABLED_NEWS_SOURCES)}]"
        response = self.index.search(query, {
            "filter": f"{published_time_filter} AND {source_filter}",
            "limit": 1000,
        })
        documents = response["hits"]
        full_articles = [
            EmbeddedArticle(
                title=doc["title"],
                url=doc["url"],
                thumbnail_url=doc["thumbnailUrl"] if "thumbnailUrl" in doc else config.DEFAULT_IMAGE_URL,
                date_published=datetime.fromtimestamp(doc["publishedTime"]),
                snippet=doc["description"],
                embeddings=doc["embeddings"],
            )
            for doc in documents
        ]
        return full_articles
