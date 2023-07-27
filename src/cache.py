
from functools import wraps
from abc import ABC, abstractmethod
import json
import time
from typing import Any, Callable, Union
from boto3.session import Session
from models import Timeline


class AbstractFunctionCache(ABC):
    """Abstract cache decorator for functions"""
    @abstractmethod
    def cache(self, cache_key_func: Callable[..., str], ttl: int = 3600) -> Callable[..., Any]:
        pass


class DynamoDBCache(AbstractFunctionCache):
    """DynamoDB Cache Backend"""
    def __init__(self, dynamodb_client: Session, table_name: str) -> None:
        self.dynamodb_client = dynamodb_client
        self.table_name = table_name

    def _parse_dict_to_timeline(self, timeline_dict: dict) -> Timeline:
        return Timeline(**timeline_dict)

    def _get_cached_result(self, cache_key: str) -> Union[Timeline, None]:
        try:
            response = self.dynamodb_client.get_item(
                TableName=self.table_name,
                Key={
                    'cache_key': {'S': cache_key}
                }
            )
            cached_data = response.get('Item', None)
            if cached_data and int(cached_data['ttl']['N']) > int(time.time()):
                timeline_dict = json.loads(cached_data['cache_value']['S'])
                return self._parse_dict_to_timeline(timeline_dict)

        except Exception as e:
            print("Error while retrieving cache:", e)

        return None

    def _store_cached_result(self, cache_key: str, result: Timeline, cache_ttl: int) -> None:
        try:
            result_dict = result.model_dump(mode="json")
            ttl = time.time() + cache_ttl
            self.dynamodb_client.put_item(
                TableName=self.table_name,
                Item={
                    'cache_key': {'S': cache_key},
                    'cache_value': {'S': json.dumps(result_dict)},
                    'ttl': {'N': str(int(ttl))}
                }
            )
        except Exception as e:
            print("Error while storing cache:", e)


    def cache(self, key_builder: Callable[..., str], ttl: int = 3600) -> Callable[..., Any]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                cache_key = key_builder(*args, **kwargs)
                cached_result = self._get_cached_result(cache_key)

                if cached_result:
                    return cached_result

                result = func(*args, **kwargs)
                self._store_cached_result(cache_key, result, ttl)
                return result

            return wrapper
        return decorator
