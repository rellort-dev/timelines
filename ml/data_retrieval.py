import requests
import pandas as pd
from os.path import exists
import csv
from urllib import parse
from config import config


MAX_CSV_LENGTH = 32000  
MAX_RESULTS_PER_PAGE = 100

def fetch_articles_from_news_api(term, sources):
    '''
    Fetches 100 articles from the past 30 days per news source.
    Returns a list of dictionaries, with each dictionary describing one article. 
    '''

    list_of_articles = []

    for source in sources:
        url = ('https://newsapi.org/v2/everything?'
                f'q={parse.quote_plus(term)}&'
                f'domains={source}&'
                f'pageSize={MAX_RESULTS_PER_PAGE}&'
                f'apiKey={config.NEWS_API_KEY}&'
                'sortBy=popularity&'
                'language=en')
        response = requests.get(url)
        print(response)
        result = response.json()['articles']
        print(f'Got {str(len(result))} results from {source}.')
        list_of_articles += result
    
    print(f'========== Got {str(len(list_of_articles))} results in total. ==========')
    return list_of_articles    


def save_articles_to_csv(list_of_articles, file_name):
    '''
    Given a list of articles in dictionary form, write and save the articles into csv.
    '''

    file_dir = f'{config.DATA_DIR}/{file_name}.csv'
    
    with open(file_dir, 'w') as csv_file:
        fieldnames = ['title', 'url', 'date_published', 'snippet', 'body']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for result in list_of_articles:
            if len(result['content']) > MAX_CSV_LENGTH: 
                result['content'] = result['content'][:MAX_CSV_LENGTH]
            writer.writerow({
                'title': result['title'],
                'url': result['url'],
                'date_published': result['publishedAt'],
                'snippet': result['description'],
                'body': result['content']
            })


def get_articles(search_term, sources=config.SOURCES):
    '''
    If articles are already cached, return them as a DataFrame. 
    Else, fetch articles published by `sources` using `search_term`,
    and save the results as a csv file with 5 columns: 
    `title`, `url`, `date_published`, `snippet`, `body`.
    '''

    file_name = search_term.replace(' ', '_')
    file_dir = f'{config.DATA_DIR}/{file_name}.csv'
    
    if not exists(file_dir):
        list_of_articles = fetch_articles_from_news_api(search_term, sources)
        save_articles_to_csv(list_of_articles, file_name)

    return pd.read_csv(file_dir)
    
