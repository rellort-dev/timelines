from datetime import date
from pydantic import BaseModel
from pydantic import HttpUrl

class Article(BaseModel):
    title: str
    url: HttpUrl
    thumbnail_url: HttpUrl
    date_published: date
    snippet: str


class Event(BaseModel):
    name: str
    date: date
    articles: list[Article]


class Timeline(BaseModel):
    events: list[Event]