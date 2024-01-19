import json
from abc import ABC, abstractmethod

import requests
from pandas import DataFrame
from transformers import pipeline


class InferenceRateLimitException(Exception):
    pass


class InferenceException(Exception):
    pass


class AbstractSummarizer(ABC):
    """Abstract client to summarize a list of articles"""

    @abstractmethod
    def __call__(self, event: DataFrame, *args, **kwargs) -> str:
        pass


class HfSummarizer(AbstractSummarizer):
    def __init__(self):
        self.hg_summarizer = pipeline(
            "summarization",
            model="google/t5-efficient-tiny",
            max_length=150,
            min_length=50,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True,
        )

    def __call__(self, event: DataFrame) -> str:
        combined_text = event.apply(lambda row: row["title"], axis=1).str.cat(sep=" ")
        res = self.hg_summarizer(combined_text)
        return res[0]["summary_text"]


class BertSummarizer(AbstractSummarizer):
    def __init__(self):
        self.summarizer = pipeline(
            "summarization",
            model="sshleifer/distilbart-xsum-12-1",
            tokenizer="sshleifer/distilbart-xsum-12-1",
            max_length=150,
            min_length=50,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True,
        )

    def __call__(self, event: DataFrame) -> str:
        combined_text = event.apply(lambda row: f'{row["title"]}. {row["snippet"]}', axis=1).str.cat(sep=". ")
        res = self.summarizer(combined_text)
        return res[0]["summary_text"]


class HfApiSummarizer(AbstractSummarizer):
    def __init__(self, model: str, api_token: str) -> None:
        self.api_token = api_token
        self.inference_url = f"https://api-inference.huggingface.co/models/{model}"

    def __call__(self, event: DataFrame) -> str:
        combined_text = event.apply(lambda row: f'{row["title"]}. {row["snippet"]}', axis=1).str.cat(sep=". ")
        response = self._request_for_summary(combined_text)
        return response[0]["summary_text"]

    def _request_for_summary(self, text: str) -> list[dict]:
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            url=self.inference_url,
            headers=headers,
            data=json.dumps(text).encode("utf-8"),
        )
        if response.status_code == 429:
            raise InferenceRateLimitException()

        return response.json()
