from __future__ import annotations

import logging
import os

import boto3


session = boto3.session.Session()
client = session.client(
    service_name="secretsmanager",
    region_name=os.environ["AWS_REGION"],
)

MEILISEARCH_URL = client.get_secret_value(SecretId="MEILISEARCH_URL")["SecretString"]
MEILISEARCH_KEY = client.get_secret_value(SecretId="MEILISEARCH_KEY")["SecretString"]

DYNAMODB_TABLE_NAME = "timelines-cache"
AWS_REGION = os.environ["AWS_REGION"]

if logging.getLogger().hasHandlers():
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
