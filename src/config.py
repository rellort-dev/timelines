import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()

IS_DEV_MODE = os.environ.get('TIMELINES_DEVELOPMENT_MODE') == 'true'

# Article settings
DISABLED_NEWS_SOURCES = os.environ["DISABLED_NEWS_SOURCES"].split(",") if os.environ["DISABLED_NEWS_SOURCES"] else ""

# Meilisearch
MEILISEARCH_URL = os.environ["MEILISEARCH_URL"]
MEILISEARCH_KEY = os.environ["MEILISEARCH_KEY"]

# CORS
ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST')]

# Cache
assert "AWS_ACCESS_KEY_ID" in os.environ
assert "AWS_SECRET_ACCESS_KEY" in os.environ
CACHE_TABLE_NAME = os.environ['CACHE_TABLE_NAME']
CACHE_TABLE_REGION = os.environ['CACHE_TABLE_REGION']
CACHE_TABLE_KEY_PREFIX = os.environ['CACHE_TABLE_KEY_PREFIX']

# Sentry
SENTRY_DSN = os.environ["SENTRY_DSN"]
SENTRY_SAMPLE_RATE = 1.0

# Development settings
if IS_DEV_MODE:
    ALLOWED_HOSTS = ['*']
    logging.basicConfig(level=logging.DEBUG)

DEFAULT_IMAGE_URL = "https://www.mxwiki.com/password/wp-content/plugins/accelerated-mobile-pages/images/SD-default-image.png"
