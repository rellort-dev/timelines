
import grequests
import logging
import validators
from typing import List
from urllib import parse

from config import config
from backend.models import Article


def remove_invalid_articles(articles):
    result = []
    for article in articles:
        props_are_valid = [
            validators.url(article["url"] if article["url"] else ""),
            validators.url(article["thumbnail_url"] if article["thumbnail_url"] else "")
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
