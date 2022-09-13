import json
import logging
import os
import pandas as pd
import grequests
from tempfile import TemporaryDirectory
from urllib import parse
from google.cloud import storage 
from google.api_core.exceptions import NotFound
from google.auth.exceptions import DefaultCredentialsError

from config import config

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
        
        cloud_file_path = self.article_folder_name + file_name
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

        cloud_file_path = self.article_folder_name + file_name
        blob = self.bucket.blob(cloud_file_path)

        with TemporaryDirectory() as temp_dir:
            temp_file_path = f'{temp_dir}/{file_name}'
            with open(temp_file_path, 'w'):
                articles.to_csv(temp_file_path, index=False)
                blob.upload_from_filename(temp_file_path)

    def get_timeline(self, file_name):
        assert file_name.endswith('.json')

        cloud_file_path = self.timeline_folder_name + file_name
        blob = self.bucket.blob(cloud_file_path)
        
        with TemporaryDirectory() as temp_dir:
            temp_file_path = f'{temp_dir}/{file_name}'
            try:
                blob.download_to_filename(temp_file_path)
            except NotFound:
                return False, None
            with open(temp_file_path) as file:
                return True, json.load(file)

    def save_timeline(self, timeline, file_name):
        assert file_name.endswith('.json')

        cloud_file_path = self.timeline_folder_name + file_name
        blob = self.bucket.blob(cloud_file_path) 
        
        with TemporaryDirectory() as temp_dir:
            temp_file_path = f'{temp_dir}/{file_name}'
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            with open(temp_file_path, 'w') as fp:
                json.dump(timeline, fp, default=str)
            blob.upload_from_filename(temp_file_path)

def fetch_articles_from_news_api(search_term, sources):
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
    
    logging.debug(f'Got {str(len(articles))} results in total.')

    articles_df = pd.DataFrame.from_records(articles)
    return articles_df
