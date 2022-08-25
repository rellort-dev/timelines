
import os
from config import config
from unittest.mock import patch

from ml.data_retrieval import fetch_articles_from_news_api, get_articles


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

