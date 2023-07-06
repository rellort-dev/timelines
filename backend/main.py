
import grequests  # Import first for monkey patching

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.dynamodb import DynamoBackend
from fastapi_cache.decorator import cache
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from backend.models import Timeline
from config import config
from ml.data_retrieval import fetch_articles_from_news_api
from ml.pipelines import sliding_window_optics_pipeline


def build_key_on_query(
    func, namespace: str = "", request: Request = None,
    response: Response = None, *args, **kwargs
):
    return ":".join([
        namespace,
        request.method.lower(),
        request.url.path,
        repr(sorted(request.query_params.items()))
    ])


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


@app.get("/timeline", response_model=Timeline)
@cache(expire=60*60*12, key_builder=build_key_on_query)
@limiter.limit('1/second')
async def get_timeline(request: Request, q: str):
    articles = fetch_articles_from_news_api(q, sources=config.SOURCES)
    events = sliding_window_optics_pipeline(articles)
    timeline = {'events': events}
    return timeline


@app.on_event("startup")
async def startup():
    dynamodb = DynamoBackend(
        table_name=config.CACHE_TABLE_NAME,
        region=config.CACHE_TABLE_REGION,
    )
    await dynamodb.init()
    FastAPICache.init(dynamodb, prefix=config.CACHE_TABLE_KEY_PREFIX)
