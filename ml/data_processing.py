import copy
from datetime import timedelta
from config import config
from .utils import daterange


def process_text_columns(df, 
                         articles_to_remove=config.ARTICLES_TO_REMOVE, 
                         contraction_map=config.CONTRACTION_MAP):
    '''
    Combines the `title`, `snippet`, and `body` columns 
    into a single processed `text` column.
    '''

    df = copy.deepcopy(df)

    # Remove articles with duplicate title, snippet, or body
    df = df.drop_duplicates(subset=['title'])
    df = df.drop_duplicates(subset=['snippet'])
    df = df.drop_duplicates(subset=['body'])
    
    # Remove articles with no title, snippet, or body
    df = df.dropna(subset=['title'])
    df = df.dropna(subset=['snippet']) 
    df = df.dropna(subset=['body'])
    
    # Remove articles that do not convey event information
    # (e.g. The Guardian's daily 'what we know on day x of the ukraine war' article series)
    mask = df.title.str.startswith(articles_to_remove)
    df = df[~mask] 
    
    # Combine text columns
    df['text'] = df.title + ' ' + df.snippet + ' ' + df.body
    
    # Convert words into lower case
    df.text = df.text.str.lower()
    
    # Convert contractions into formal form
    df.text = df.text.replace(contraction_map, regex=True)

    # Remove HTML tags
    df.text = df.text.str.replace(r'<[^<>]*>', '', regex=True)
    
    # Remove everything in parenthesis
    df.text = df.text.str.replace(r'\([^\(\)]*\)', '', regex=True)
    df.text = df.text.str.replace(r'\[[^\[\]]*\]', '', regex=True)

    # Remove words or phrases that convey no meaning    
    news_agencies = ['cnbc', 'the washington post', 'the associated press', 'reuters.com',
                     'reuters', 'read more at straitstimes.com.', 'bbc news']
    boilerplate_text = ['placeholder while article actions load', 'posted',  
                        'image source',  'getty images', 'image caption',  'good morning and welcome to the climate 202']
    for meaningless_string in (news_agencies + boilerplate_text):
        df.text = df.text.str.replace(meaningless_string, '', regex=True)
    
    # Remove non-alphanumeric characters
    df.text = df.text.str.replace('[^a-zA-Z0-9]', ' ', regex=True)
    
    # Remove duplicate spaces
    df.text = df.text.str.replace(' +', ' ', regex=True)
    
    # Remove trailing and leading spaces 
    df.text = df.text.str.strip()
    
    return df


def partition_data_into_windows(df, window_delta=0, step=1):
    '''
    Returns a list of DataFrames, where each DataFrame contains 
    articles published on some day += window_delta. 

    Examples: 
        Parameters           Days contained in each window
    window_delta=0, step=1 --> [4-4, 5-5, 6-6, ...]
    window_delta=1, step=1 --> [3-5, 4-6, 5-7, ...]
    window_delta=2, step=1 --> [2-6, 3-7, 4-8, ...]
    window_delta=0, step=2 --> [4-4, 6-6, 8-8, ...]
    '''

    windows = []

    window_size = timedelta(days=window_delta)
    start_date = df.date_published.dt.date.min()
    end_date = df.date_published.dt.date.max()

    for d in daterange(start_date + window_size,
                       end_date - window_size + timedelta(days=1), 
                       timedelta(days=step)):
        lower_bound = d - window_size 
        upper_bound = d + window_size
        is_within_window = (lower_bound <= df.date_published.dt.date) & (df.date_published.dt.date <= upper_bound)
        data_within_window = df[is_within_window]
        windows.append(data_within_window)
    
    return windows
