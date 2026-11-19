from custom_requester.custom_requester import CustomRequester


class MoviesAPI(CustomRequester):
    ENDPOINT = "/movies"

    def get_movies(self, params=None, expected_status=200):
        return self.send_request(
            "GET",
            self.ENDPOINT,
            params=params,
            expected_status=expected_status,
        )

    def create_movie(self, data, expected_status=201):
        return self.send_request(
            "POST", self.ENDPOINT, data=data, expected_status=expected_status
        )

    def get_movie(self, movie_id, expected_status=200):
        return self.send_request(
            "GET",
            f"{self.ENDPOINT}/{movie_id}",
            expected_status=expected_status,
        )

    def update_movie(self, movie_id, data, expected_status=200):
        return self.send_request(
            "PATCH",
            f"{self.ENDPOINT}/{movie_id}",
            data=data,
            expected_status=expected_status,
        )

    def delete_movie(self, movie_id, expected_status=200):
        return self.send_request(
            "DELETE",
            f"{self.ENDPOINT}/{movie_id}",
            expected_status=expected_status,
        )
