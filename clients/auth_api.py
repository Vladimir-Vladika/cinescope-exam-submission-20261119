from custom_requester.custom_requester import CustomRequester


class AuthAPI(CustomRequester):
    def login(self, email, password, expected_status=200):
        return self.send_request('POST', '/login', data={'email': email, 'password': password}, expected_status=expected_status)
