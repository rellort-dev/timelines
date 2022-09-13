
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from backend.models import Timeline
from config import config
from ml.data_retrieval import Storage, fetch_articles_from_news_api
from ml.pipelines import sliding_window_optics_pipeline

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_HOSTS,
    allow_methods=['*'],
    allow_headers=['*']
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

storage = Storage()

@app.get("/timeline", response_model=Timeline)
@limiter.limit('1/second')
async def get_timeline(request: Request, q: str):
    timeline_file_name = f'{q.replace(" ", "_")}.json'
    timeline_is_cached, timeline = storage.get_timeline(timeline_file_name)
    if timeline_is_cached:
        return timeline

    articles = fetch_articles_from_news_api(q, sources=config.SOURCES)
    events = sliding_window_optics_pipeline(articles)
    timeline = {'events': events}

    storage.save_timeline(timeline, timeline_file_name)  # TODO: make this async
    return timeline
