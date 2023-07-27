from __future__ import annotations

import logging
from datetime import datetime
from datetime import timedelta

import config
from models import Timeline
from news_client import MeilisearchNewsClient
from pipelines import SlidingWindowOpticsPipeline


news_client = MeilisearchNewsClient(
    meilisearch_url=config.MEILISEARCH_URL,
    meilisearch_key=config.MEILISEARCH_KEY,
    index_name="articles",
)
pipeline = SlidingWindowOpticsPipeline()


def get_timeline(query: str):
    today = datetime.now()
    two_weeks_ago = today - timedelta(days=14)
    embedded_articles = news_client.fetch_news(
        query=query,
        before=today,
        after=two_weeks_ago,
    )
    events = pipeline.generate_events(articles=embedded_articles)
    timeline = {"events": events}
    return timeline


def get_query_string(event: dict) -> str:
    return event["queryStringParameters"]["q"]


def create_response(timeline: Timeline) -> dict:
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "isBase64Encoded": False,
        "body": timeline,
    }


def lambda_handler(event):
    logging.log("Lambda invoked. Getting query string.")
    query = get_query_string(event)
    logging.log("Getting timeline.")
    timeline = get_timeline(query)
    logging.log("Creating response.")
    return create_response(timeline)
