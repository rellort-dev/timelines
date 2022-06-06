import requests
import csv

API_KEY = '7a55c116-c8c7-4459-89a6-2038ab0d39d1'

page_size = 200
term = 'ukraine war'.replace(' ', '%20')
from_date = '2022-05-06'
to_date = '2022-06-06'
response = requests.get(f'https://content.guardianapis.com/search?from-date={from_date}&to-date={to_date}&show-fields=trailText%2CbodyText%2C%20&page-size={page_size}&q={term}&api-key={API_KEY}')
results = response.json()['response']['results']


def write_search_results_to_csv(results, file_name):
    with open(f'{file_name}.csv', 'w') as csv_file:
        fieldnames = ['title', 'url', 'date_published', 'snippet', 'text']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({
                'title': result['webTitle'],
                'url': result['webUrl'],
                'date_published': result['webPublicationDate'],
                'snippet': result['fields']['trailText'],
                'text': result['fields']['bodyText']
            })

write_search_results_to_csv(results, 'guardian')