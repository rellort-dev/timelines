
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import Timeline
from config import config
from ml.data_retrieval import Storage, fetch_articles_from_news_api
from ml.pipelines import sliding_window_optics_pipeline


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_HOSTS,
    allow_methods=['*'],
    allow_headers=['*']
)

storage = Storage()

@app.get("/timeline", response_model=Timeline)
async def get_timeline(q: str):

    timeline_file_name = f'{q.replace(" ", "_")}.json'
    timeline_is_cached, timeline = storage.get_timeline(timeline_file_name)
    if timeline_is_cached:
        return timeline
        
    articles = fetch_articles_from_news_api(q, sources=config.SOURCES)
    events = sliding_window_optics_pipeline(articles)
    timeline = {'events': events}
    storage.save_timeline(timeline, timeline_file_name)  # TODO: make this async
    return timeline
