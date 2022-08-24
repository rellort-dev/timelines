
import os
from config import config
from unittest.mock import patch

from ml.data_retrieval import fetch_articles_from_news_api, get_articles

class TestFetchArticlesFromNewsApi:
    @classmethod
    def setup_class(cls):
        cls.default_term = 'American economy'
        cls.articles = fetch_articles_from_news_api(cls.default_term, config.SOURCES[:3])

    @classmethod
    def teardown_class(cls):
        pass

    def test_fetch(self): 
        for article in self.articles: 
            assert article.keys() == {'source', 'author', 'title', 'description', 
                                      'url', 'urlToImage', 'publishedAt', 'content'}

    def test_sources(self): 
        nytimes_only = ['nytimes.com']
        articles = fetch_articles_from_news_api(self.default_term, nytimes_only)
        for article in articles: 
            assert article['source']['name'] == 'New York Times'
            assert article['url'].startswith('https://www.nytimes.com/')

    def test_length(self):
         assert len(self.articles) > 0


class TestGetArticles: 
    @classmethod
    def setup_class(cls):
        cls.default_term = 'American economy'

    def test_cache(self): 
        get_articles(self.default_term)
        with patch('ml.data_retrieval.fetch_articles_from_news_api', 
                   return_value=[]) as mock_method:
            get_articles(self.default_term)
            mock_method.assert_not_called()

