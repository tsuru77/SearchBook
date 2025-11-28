from functools import lru_cache

from elasticsearch import Elasticsearch

from app.core.config import settings


@lru_cache
def get_elasticsearch_client() -> Elasticsearch:
    return Elasticsearch(
        settings.elasticsearch_host,
        basic_auth=(settings.elasticsearch_username, settings.elasticsearch_password),
        verify_certs=False,
    )


