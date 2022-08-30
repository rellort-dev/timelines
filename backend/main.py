
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import Timeline
from config.config import ALLOWED_HOSTS
from ml.data_retrieval import get_articles
from ml.pipelines import sliding_window_optics_pipeline


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get("/timeline", response_model=Timeline)
async def get_timeline(q: str):
    try:
        articles = get_articles(q)
    except ValueError:
        # There is an invalid API key.
        raise HTTPException(status_code=503, detail='Server is unavailable now, please try again later')

    events = sliding_window_optics_pipeline(articles)
    return {"events": events}
    