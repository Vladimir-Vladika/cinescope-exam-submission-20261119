from clients.auth_api import AuthAPI
from clients.genres_api import GenresAPI
from clients.movies_api import MoviesAPI


class ApiManager:
    def __init__(self, session, settings):
        self.movies_api = MoviesAPI(session, settings.movies_url, settings.timeout)
        self.genres_api = GenresAPI(session, settings.movies_url, settings.timeout)
        self.auth_api = AuthAPI(session, settings.auth_url, settings.timeout)
