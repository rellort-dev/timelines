import pandas as pd
import os

# Ref: https://github.com/dipanjanS/text-analytics-with-python/blob/master/New-Second-Edition/Ch05%20-%20Text%20Classification/contractions.py
CONTRACTION_MAP = {
    "ain't": "is not",
    "aren't": "are not",
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'd've": "he would have",
    "he'll": "he will",
    "he'll've": "he he will have",
    "he's": "he is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how is",
    "I'd": "I would",
    "I'd've": "I would have",
    "I'll": "I will",
    "I'll've": "I will have",
    "I'm": "I am",
    "I've": "I have",
    "i'd": "i would",
    "i'd've": "i would have",
    "i'll": "i will",
    "i'll've": "i will have",
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it'd": "it would",
    "it'd've": "it would have",
    "it'll": "it will",
    "it'll've": "it will have",
    "it's": "it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she would",
    "she'd've": "she would have",
    "she'll": "she will",
    "she'll've": "she will have",
    "she's": "she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so as",
    "that'd": "that would",
    "that'd've": "that would have",
    "that's": "that is",
    "there'd": "there would",
    "there'd've": "there would have",
    "there's": "there is",
    "they'd": "they would",
    "they'd've": "they would have",
    "they'll": "they will",
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what will",
    "what'll've": "what will have",
    "what're": "what are",
    "what's": "what is",
    "what've": "what have",
    "when's": "when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where is",
    "where've": "where have",
    "who'll": "who will",
    "who'll've": "who will have",
    "who's": "who is",
    "who've": "who have",
    "why's": "why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you would",
    "you'd've": "you would have",
    "you'll": "you will",
    "you'll've": "you will have",
    "you're": "you are",
    "you've": "you have"
}

# Augment contraction map with alternative apostrophe used by some news outlets
for contraction in list(CONTRACTION_MAP):
    CONTRACTION_MAP[contraction.replace("'", "’")] = CONTRACTION_MAP[contraction]

def process_text_columns(df):
    '''
    Combines the `title`, `snippet`, and `body` columns 
    into a single processed `text` column.
    '''

    # Remove articles with duplicate title, snippet, or body
    df = df.drop_duplicates(subset=['title'])
    df = df.drop_duplicates(subset=['snippet'])
    df = df.drop_duplicates(subset=['body'])
    
    # Remove articles with no title, snippet, or body
    df = df.dropna(subset=['title'])
    df = df.dropna(subset=['snippet']) 
    df = df.dropna(subset=['body'])
    
    # Remove series of articles 
    # (e.g. The Guardian's daily article series 'what we know on day x of the ukraine war')
    articles_to_remove = df.title.str.startswith((
        'russia-ukraine war: what we know on day',  # The Guardian
        'timeline: week',  # Al Jazeera
        'russia-ukraine war: list of key events, day',  # Al Jazeera
        'russia-ukraine war: what happened',  # NPR
    ))
    df = df[~articles_to_remove] 
    
    # Combine text columns
    df['text'] = df.title + ' ' + df.snippet + ' ' + df.body
    
    # Convert words into lower case
    df.text = df.text.str.lower()
    
    # Convert contractions into formal form
    df.title = df.title.replace(CONTRACTION_MAP, regex=True)

    # Remove HTML tags
    df.text = df.text.str.replace(r'<[^<>]*>', '', regex=True)
    
    # Remove everything in parenthesis
    df.text = df.text.str.replace(r'\([^\(\)]*\)', '', regex=True)
    df.text = df.text.str.replace(r'\[[^\[\]]*\]', '', regex=True)

    # Remove words or phrases that convey no meaning    
    news_agencies = ['cnbc', 'the washington post', 'the associated press', 'reuters.com',
                     'reuters', 'read more at straitstimes.com.', 'bbc news']
    boilerplate_text =['placeholder while article actions load', 'posted',  
                       'image source',  'getty images', 'image caption',  'good morning and welcome to the climate 202']
    for meaningless_string in (news_agencies + boilerplate_text):
        df.text = df.text.str.replace(meaningless_string, '', regex=True)
    
    # Remove non-alphanumeric characters
    df.text = df.text.str.replace('[^a-zA-Z0-9]', ' ', regex=True)
    
    # Remove duplicate spaces
    df.text = df.text.str.replace(' +', ' ', regex=True)
    
    return df
