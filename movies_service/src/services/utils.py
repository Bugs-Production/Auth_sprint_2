from typing import Any


def get_offset_params(page_num: int, page_size: int) -> dict[str, int]:
    """Параметры для запроса в Elastic с offset параметрами"""
    offset = (page_num - 1) * page_size
    return {
        "from": offset,
        "size": page_size,
    }


def get_sort_params(sorting: str) -> dict[str, list[dict[str, str]]]:
    """Параметры для запроса в Elastic с сортировкой по рейтингу"""

    return {
        "sort": [{"imdb_rating": "desc" if sorting.startswith("-") else "asc"}],
    }


def get_genre_filter_params(genre_filter: str | None) -> dict[str, Any]:
    """Параметры для запроса в Elastic с фильтрацией по жанру"""

    genre_params = {"query": {}}
    if genre_filter:
        genre_params["query"] = {
            "nested": {
                "path": "genres",
                "query": {"bool": {"should": [{"match": {"genres.id": genre_filter}}]}},
            }
        }
    else:
        genre_params["query"] = {"match_all": {}}

    return genre_params


def get_match_params(field_to_query: dict) -> dict:
    must_clauses = []

    for field, value in field_to_query.items():
        must_clause = {"match": {field: value}}
        must_clauses.append(must_clause)

    query = {"query": {"bool": {"must": must_clauses}}}

    return query
