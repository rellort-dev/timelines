from __future__ import annotations

from datetime import date  # noqa: F401
from datetime import datetime

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


class Timeline(BaseModel):
    events: list[Event]
