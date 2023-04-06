
import grequests
import json
import logging
import os
import pandas as pd
import validators
from google.cloud import storage 
from google.api_core.exceptions import NotFound
from google.auth.exceptions import DefaultCredentialsError
from tempfile import TemporaryDirectory
from typing import List, Tuple
from urllib import parse

from config import config
from backend.models import Article, Timeline

class Storage:
    
    def __init__(self):
        try:
            storage_client = storage.Client()
        except DefaultCredentialsError:
            message = 'Unable to connect to cloud storage. ' \
                + 'Check the GOOGLE_APPLICATION_CREDENTIALS environment variable.'
            logging.debug(message)
            raise ValueError(message)
        self.bucket = storage_client.bucket(config.GOOGLE_CLOUD_BUCKET_NAME)
        
        self.article_folder_name = config.get_articles_folder_name()
        self.timeline_folder_name = config.get_timeline_folder_name()
    
    def get_articles(self, file_name):
        assert file_name.endswith('.csv')
        
        cloud_file_path = f'{self.article_folder_name}/{file_name}'
        blob = self.bucket.blob(cloud_file_path)
        
        with TemporaryDirectory() as temp_dir:
            temp_file_path = f'{temp_dir}/{file_name}'
            with open(temp_file_path, 'w'):
                try: 
                    blob.download_to_filename(temp_file_path)
                    return True, pd.read_csv(temp_file_path)
                except NotFound:
                    return False, None

    def save_articles(self, articles, file_name):
        assert file_name.endswith('.csv')

        cloud_file_path = f'{self.article_folder_name}/{file_name}'
        blob = self.bucket.blob(cloud_file_path)

        with TemporaryDirectory() as temp_dir:
            temp_file_path = f'{temp_dir}/{file_name}'
            with open(temp_file_path, 'w'):
                articles.to_csv(temp_file_path, index=False)
                blob.upload_from_filename(temp_file_path)

    def get_timeline(self, file_name: str) -> Tuple[bool, Timeline]:
        assert file_name.endswith('.json')

        cloud_file_path = f'{self.timeline_folder_name}/{file_name}'
        blob = self.bucket.blob(cloud_file_path)
        
        with TemporaryDirectory() as temp_dir:
            temp_file_path = f'{temp_dir}/{file_name}'
            try:
                blob.download_to_filename(temp_file_path)
            except NotFound:
                return False, None
            with open(temp_file_path) as file:
                return True, json.load(file)

    def save_timeline(self, timeline: Timeline, file_name: str):
        assert file_name.endswith('.json')

        cloud_file_path = f'{self.timeline_folder_name}/{file_name}'
        blob = self.bucket.blob(cloud_file_path) 
        
        with TemporaryDirectory() as temp_dir:
            temp_file_path = f'{temp_dir}/{file_name}'
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            with open(temp_file_path, 'w') as fp:
                json.dump(timeline, fp, default=str)
            blob.upload_from_filename(temp_file_path)


def remove_invalid_articles(articles):
    result = []
    for article in articles:
        props_are_valid = [
            validators.url(article["url"]),
            validators.url(article["thumbnail_url"])
        ]
        if all(props_are_valid):
            result.append(article)
        else:
            logging.warning(f"Invalid article returned from data source: {article['url']}")
    return result


def fetch_articles_from_news_api(search_term: str, sources: str) -> List[Article]:
    '''
    Fetch and return a DataFrame of news articles (maximum 100 articles per news source).
    Articles are all published within the last 30 days.
    '''

    MAX_RESULTS_PER_PAGE = 100
    articles = []

    urls = [('https://newsapi.org/v2/everything?'
                f'q={parse.quote_plus(search_term)}&'
                f'domains={source}&'
                f'pageSize={MAX_RESULTS_PER_PAGE}&'
                f'apiKey={config.NEWS_API_KEY}&'
                'sortBy=popularity&'
                'language=en')
            for source in sources]
    responses = (grequests.get(url) for url in urls)
    
    for response in grequests.imap(responses):
        if 'articles' not in response.json():
            message = 'Unable to fetch articles from source. Check your API key.'
            logging.debug(message)
            raise ValueError(message)

        results = response.json()['articles']

        for result in results:
            articles.append({
                'title': result['title'],
                'url': result['url'],
                'thumbnail_url': result['urlToImage'],
                'date_published': result['publishedAt'],
                'snippet': result['description'],
                'body': result['content']
            })
    
    valid_articles = remove_invalid_articles(articles)

    total_num_articles = len(articles)
    num_invalid_articles = total_num_articles - len(valid_articles)
    logging.debug(f'Got {total_num_articles} results in total. ({num_invalid_articles} invalid)')

    return valid_articles
