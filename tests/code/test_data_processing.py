
from datetime import timedelta
import pandas as pd
import pytest
from config import config
from ml.data_processing import partition_data_into_windows, process_text_columns

@pytest.fixture(scope="module")
def df():
    return pd.read_csv(f'{config.FIXTURES_DIR}/raw_articles.csv')

def test_process_text_columns(df):
    processed_df = process_text_columns(df)
    assert processed_df.text.str.islower().all()
    processed_text_without_spaces = processed_df.text.str.replace(' ', '')
    assert processed_text_without_spaces.str.isalnum().all()

@pytest.mark.parametrize(
    "window_delta, step",
    [
        (0, 1), 
        (1, 1),
        (2, 1),
        (0, 2)
    ],
)
def test_partition_data_into_windows(df, window_delta, step):
    df.date_published = pd.to_datetime(df.date_published)
    sliding_windows = partition_data_into_windows(df, window_delta, step)
    for window in sliding_windows: 
        assert max(window.date_published.dt.date) -  min(window.date_published.dt.date) <= timedelta(days=2 * window_delta)
