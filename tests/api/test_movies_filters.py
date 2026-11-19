import pytest

pytestmark = [pytest.mark.api, pytest.mark.admin]


def test_filter_by_price(api_manager, generator, genre_id, tracked_create):
    lower, upper = 350, 650
    prices = sorted({lower - 1, lower, (lower + upper) // 2, upper, upper + 1})
    owned = {}
    for price in prices:
        movie = tracked_create(
            generator.movie(genre_id, price=price, location="MSK")
        ).json()
        owned[movie["id"]] = price

    params = {
        "minPrice": lower,
        "maxPrice": upper,
        "genreId": genre_id,
        "locations": ["MSK"],
        "published": "true",
        "pageSize": 20,
        "createdAt": "desc",
    }
    seen = set()
    page = 1
    while True:
        body = api_manager.movies_api.get_movies(
            {**params, "page": page}
        ).json()
        for movie in body["movies"]:
            assert lower <= movie["price"] <= upper
            assert movie["location"] == "MSK"
            assert movie["published"] is True
            assert movie["genreId"] == genre_id
            seen.add(movie["id"])
        if page >= body["pageCount"]:
            break
        page += 1
        assert page <= 1000, "Unexpectedly large dataset; stop pagination"

    expected = {
        movie_id
        for movie_id, price in owned.items()
        if lower <= price <= upper
    }
    excluded = set(owned) - expected
    assert expected <= seen, (
        f"Filter omitted matching owned movies: {expected - seen}"
    )
    assert not excluded & seen, "Filter included out-of-range owned movies"
