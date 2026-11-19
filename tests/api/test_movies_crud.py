import pytest

pytestmark = [pytest.mark.api, pytest.mark.admin]


def assert_movie_matches(actual, expected):
    for field, value in expected.items():
        assert actual[field] == value, f'{field}: expected {value!r}, got {actual[field]!r}'


@pytest.mark.smoke
def test_create_movie(tracked_create, movie_data, api_manager):
    created = tracked_create(movie_data).json()
    assert isinstance(created['id'], int)
    assert_movie_matches(created, movie_data)
    saved = api_manager.movies_api.get_movie(created['id']).json()
    assert saved['id'] == created['id']
    assert_movie_matches(saved, movie_data)


def test_get_movie(created_movie, api_manager):
    body = api_manager.movies_api.get_movie(created_movie['id']).json()
    assert body['id'] == created_movie['id']
    assert_movie_matches(body, created_movie['data'])
    assert isinstance(body['reviews'], list)


@pytest.mark.parametrize('field', ['name', 'price', 'description', 'location', 'published', 'genreId'])
def test_create_missing_required_field(tracked_create, movie_data, field):
    movie_data.pop(field)
    tracked_create(movie_data, expected_status=400)


@pytest.mark.parametrize('field,value', [('price', 'not-a-number'), ('location', 'INVALID'), ('published', 'not-a-boolean')])
def test_create_invalid_field(tracked_create, movie_data, field, value):
    movie_data[field] = value
    tracked_create(movie_data, expected_status=400)


def test_duplicate_name(tracked_create, created_movie):
    tracked_create(created_movie['data'], expected_status=409)


@pytest.mark.smoke
def test_patch_movie(admin_api, api_manager, created_movie):
    original = created_movie['data']
    changes = {'price': original['price'] + 1, 'description': original['description'] + ' Updated.'}
    response = admin_api.movies_api.update_movie(created_movie['id'], changes).json()
    assert response['id'] == created_movie['id']
    assert_movie_matches(response, {**original, **changes})
    saved = api_manager.movies_api.get_movie(created_movie['id']).json()
    assert_movie_matches(saved, {**original, **changes})


def test_patch_invalid_data_does_not_change_movie(admin_api, api_manager, created_movie):
    admin_api.movies_api.update_movie(created_movie['id'], {'location': 'INVALID'}, expected_status=400)
    saved = api_manager.movies_api.get_movie(created_movie['id']).json()
    assert_movie_matches(saved, created_movie['data'])


@pytest.mark.smoke
def test_delete_movie(admin_api, api_manager, created_movie):
    body = admin_api.movies_api.delete_movie(created_movie['id']).json()
    assert body['id'] == created_movie['id']
    api_manager.movies_api.get_movie(created_movie['id'], expected_status=404)


@pytest.mark.parametrize('operation', ['get', 'patch', 'delete'])
def test_missing_movie(admin_api, api_manager, created_movie, operation):
    # Use an ID we created and deleted, never a guessed ID of another student's movie.
    movie_id = created_movie['id']
    admin_api.movies_api.delete_movie(movie_id)
    if operation == 'get':
        api_manager.movies_api.get_movie(movie_id, expected_status=404)
    elif operation == 'patch':
        admin_api.movies_api.update_movie(movie_id, {'price': 500}, expected_status=404)
    else:
        admin_api.movies_api.delete_movie(movie_id, expected_status=404)


@pytest.mark.parametrize('operation', ['patch', 'delete'])
def test_mutation_requires_authentication(api_manager, created_movie, operation):
    movie_id = created_movie['id']
    if operation == 'patch':
        api_manager.movies_api.update_movie(movie_id, {'price': 500}, expected_status=401)
    else:
        api_manager.movies_api.delete_movie(movie_id, expected_status=401)
    saved = api_manager.movies_api.get_movie(movie_id).json()
    assert_movie_matches(saved, created_movie['data'])
