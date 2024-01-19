from datetime import datetime, timedelta

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.dynamodb import DynamoBackend
from fastapi_cache.decorator import cache
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import config
from models import Timeline
from news_client import MeilisearchNewsClient
from pipelines import SlidingWindowOpticsPipeline
from summarizers import HfApiSummarizer

sentry_sdk.init(dsn=config.SENTRY_DSN, traces_sample_rate=config.SENTRY_SAMPLE_RATE)

news_client = MeilisearchNewsClient(
    meilisearch_url=config.MEILISEARCH_URL,
    meilisearch_key=config.MEILISEARCH_KEY,
    index_name="articles",
)

summarizer = HfApiSummarizer(model="facebook/bart-large-cnn", api_token=config.HUGGING_FACE_KEY)
pipeline = SlidingWindowOpticsPipeline(summarizer)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=config.ALLOWED_HOSTS, allow_methods=["*"], allow_headers=["*"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/timeline", response_model=Timeline)
@cache(expire=60 * 60 * 12)
@limiter.limit("1/second")
async def get_timeline(request: Request, q: str):
    today = datetime.now()
    two_weeks_ago = today - timedelta(days=14)
    embedded_articles = news_client.fetch_news(
        query=q,
        before=today,
        after=two_weeks_ago,
    )
    events = pipeline.generate_events(articles=embedded_articles)
    timeline = {"events": events}
    return timeline


@app.on_event("startup")
async def startup():
    dynamodb = DynamoBackend(
        table_name=config.CACHE_TABLE_NAME,
        region=config.CACHE_TABLE_REGION,
    )
    await dynamodb.init()
    FastAPICache.init(dynamodb, prefix="")
