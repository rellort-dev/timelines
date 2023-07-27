from __future__ import annotations

from datetime import datetime
from datetime import timedelta
import json

import boto3
import config
from cache import DynamoDBCache
from config import logger
from models import Timeline
from news_client import MeilisearchNewsClient
from pipelines import SlidingWindowOpticsPipeline
from utils import store_locally, build_key_on_query


news_client = MeilisearchNewsClient(
    meilisearch_url=config.MEILISEARCH_URL,
    meilisearch_key=config.MEILISEARCH_KEY,
    index_name="articles",
)
pipeline = SlidingWindowOpticsPipeline()
dynamodb_client = boto3.client("dynamodb", region_name=config.AWS_REGION)
dynamodb_cache = DynamoDBCache(
    dynamodb_client=dynamodb_client,
    table_name=config.DYNAMODB_TABLE_NAME,
)



@dynamodb_cache.cache(key_builder=build_key_on_query, ttl=4 * 60 * 60)
def get_timeline(query: str) -> Timeline:
    today = datetime.now()
    two_weeks_ago = today - timedelta(days=14)

    logger.info(f"Fetching news articles for {query} in range [{two_weeks_ago}, {today}]")
    embedded_articles = news_client.fetch_news(
        query=query,
        before=today,
        after=two_weeks_ago,
    )

    logger.info("Generating events")
    events = pipeline.generate_events(articles=embedded_articles)
    timeline = Timeline(events=events)
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
        "body": json.dumps(timeline.model_dump(mode="json")),
    }


def lambda_handler(event, context):
    logger.info("Lambda invoked. Getting query string.")
    query = get_query_string(event)

    logger.info("Getting timeline.")
    timeline = get_timeline(query)

    logger.info("Creating response.")
    return create_response(timeline)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q",
        "--query",
        help="Query string",
    )
    args = vars(parser.parse_args())
    query = str(args.get("query"))

    timeline = get_timeline(query)
    store_locally(timeline, query)
