import math

import pytest

pytestmark = [pytest.mark.api, pytest.mark.public]


@pytest.mark.smoke
def test_get_movies(api_manager):
    body = api_manager.movies_api.get_movies({"page": 1, "pageSize": 3}).json()
    assert isinstance(body["movies"], list)
    assert body["page"] == 1
    assert body["pageSize"] == 3
    assert 0 <= len(body["movies"]) <= 3
    assert body["count"] >= len(body["movies"])
    assert body["pageCount"] == math.ceil(body["count"] / 3)
    for movie in body["movies"]:
        assert isinstance(movie["id"], int)
        assert isinstance(movie["name"], str)
        assert isinstance(movie["price"], (int, float))


@pytest.mark.parametrize(
    "params",
    [
        {"page": "abc"},
        {"page": 0},
        {"pageSize": 0},
        {"pageSize": 21},
        {"minPrice": "abc"},
        {"maxPrice": "abc"},
        {"locations": "INVALID"},
        {"createdAt": "INVALID"},
    ],
    ids=[
        "page-text",
        "page-zero",
        "size-zero",
        "size-too-large",
        "min-text",
        "max-text",
        "location",
        "sort",
    ],
)
def test_invalid_list_parameters(api_manager, params):
    api_manager.movies_api.get_movies(params, expected_status=400)


def test_create_requires_authentication(api_manager, movie_data):
    api_manager.movies_api.create_movie(movie_data, expected_status=401)
