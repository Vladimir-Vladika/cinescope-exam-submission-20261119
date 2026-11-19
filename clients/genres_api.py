from custom_requester.custom_requester import CustomRequester


class GenresAPI(CustomRequester):
    def get_genres(self):
        return self.send_request('GET', '/genres')
