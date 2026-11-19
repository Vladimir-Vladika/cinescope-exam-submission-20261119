import pytest
import requests

from clients.api_manager import ApiManager
from config.settings import Settings
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator


@pytest.fixture(scope='session')
def settings():
    return Settings.from_env()


@pytest.fixture
def api_manager(settings):
    with requests.Session() as session:
        yield ApiManager(session, settings)


@pytest.fixture(scope='session')
def admin_token(settings):
    if settings.admin_token:
        return settings.admin_token
    if not (settings.admin_email and settings.admin_password):
        pytest.fail('Set ADMIN_EMAIL and ADMIN_PASSWORD (SUPER_ADMIN), or ADMIN_TOKEN, in .env', pytrace=False)
    with requests.Session() as session:
        manager = ApiManager(session, settings)
        body = manager.auth_api.login(settings.admin_email, settings.admin_password).json()
    assert 'SUPER_ADMIN' in body['user']['roles'], 'Account must have the SUPER_ADMIN role'
    assert body.get('accessToken'), 'Login did not return accessToken'
    return body['accessToken']


@pytest.fixture
def admin_api(settings, admin_token):
    # Separate function-scoped sessions prevent auth leaking into public tests.
    with requests.Session() as session:
        session.headers.update({'Authorization': f'Bearer {admin_token}'})
        yield ApiManager(session, settings)


@pytest.fixture
def generator():
    return DataGenerator()


@pytest.fixture
def genre_id(api_manager):
    genres = api_manager.genres_api.get_genres().json()
    assert isinstance(genres, list) and genres, 'The test environment needs at least one genre'
    return genres[0]['id']


@pytest.fixture
def movie_data(generator, genre_id):
    return generator.movie(genre_id)


@pytest.fixture
def tracked_create(admin_api):
    """Register successful creations BEFORE asserting the expected status."""
    ids = set()

    def create(data, expected_status=201):
        response = admin_api.movies_api.create_movie(data, expected_status=None)
        if response.ok:
            movie_id = response.json().get('id')
            if movie_id is not None:
                ids.add(movie_id)
        CustomRequester.check_status(response, expected_status)
        return response

    yield create
    failures = []
    for movie_id in ids:
        try:
            response = admin_api.movies_api.delete_movie(movie_id, expected_status=None)
            # A deletion test may already have deleted this particular resource.
            if response.status_code not in (200, 404):
                failures.append(f'{movie_id}: HTTP {response.status_code}')
        except requests.RequestException as error:
            failures.append(f'{movie_id}: {type(error).__name__}')
    if failures:
        pytest.fail('Cleanup failed for owned movies: ' + ', '.join(failures), pytrace=False)


@pytest.fixture
def created_movie(tracked_create, movie_data):
    movie = tracked_create(movie_data).json()
    return {'id': movie['id'], 'data': movie_data, 'response': movie}
