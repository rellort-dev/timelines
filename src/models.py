from datetime import date, datetime
from pydantic import BaseModel
from pydantic import HttpUrl


class Article(BaseModel):
    title: str
    url: HttpUrl
    thumbnail_url: HttpUrl
    date_published: datetime
    snippet: str


class EmbeddedArticle(Article):
    embeddings: list[float]


class Event(BaseModel):
    name: str
    date: date
    articles: list[Article]
    summary: str


class Timeline(BaseModel):
    events: list[Event]
