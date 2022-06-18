import requests
import pandas as pd
import csv
from urllib import parse 
from process_data import process_text_columns


API_KEY = 'e01547ade4c941e794ffb554c9a98d86'
MAX_CSV_LENGTH = 32000  
MAX_RESULTS_PER_PAGE = 100

def get_list_of_articles(term, sources):
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
                f'apiKey={API_KEY}&'
                'sortBy=popularity&'
                'language=en')
        response = requests.get(url)
        result = response.json()['articles']
        print(f'Got {str(len(result))} results from {source}.')
        list_of_articles += result
    
    print(f'========== Got {str(len(list_of_articles))} results in total. ==========')
    return list_of_articles    


def save_articles_to_csv(list_of_articles, file_name):
    '''
    Given a list of articles in dictionary form, write and save the articles into csv.
    '''
    
    with open(f'../data/{file_name}.csv', 'w') as csv_file:
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

def get_and_save_articles(search_term, sources):
    '''
    Search for articles using `search_term`, published by `sources`, 
    and saves the results as a csv file with 5 columns: 
    `title`, `url`, `date_published`, `snippet`, `body`.
    '''
    list_of_articles = get_list_of_articles(search_term, sources)
    filename = search_term.replace(' ', '_')
    save_articles_to_csv(list_of_articles, filename)


def get_and_save_articles_with_parsed_text(search_term, sources):
    '''
    Search for articles using `search_term`, published by `sources`, 
    and saves the results as a csv file with 6 columns: 
    `title`, `url`, `date_published`, `snippet`, `body`, `text`. 
    '''
    get_and_save_articles(search_term, sources) 
    filename = search_term.replace(' ', '_')

    df = pd.read_csv(f'../data/{filename}.csv')
    processed_df = process_text_columns(df).
    processed_df.to_csv(f'../data/{filename}.csv', index=False)
    

sources = ['economist.com', 'apnews.com','reuters.com','theguardian.com',
           'washingtonpost.com','aljazeera.com', 'npr.org', 'nytimes.com',
           'bbc.co.uk', 'straitstimes.com']
search_term = 'inflation usa'

get_and_save_articles_with_parsed_text(search_term, sources)

