import logging

LOGGER = logging.getLogger(__name__)


class CustomRequester:
    """HTTP transport shared by domain clients; callers own the Session."""

    def __init__(self, session, base_url, timeout=30):
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def send_request(
        self, method, endpoint, data=None, params=None, expected_status=200
    ):
        url = self.base_url + "/" + endpoint.lstrip("/")
        # Bodies, cookies and headers may contain authentication secrets.
        LOGGER.info("%s %s", method, url)
        response = self.session.request(
            method=method,
            url=url,
            json=data,
            params=params,
            timeout=self.timeout,
            allow_redirects=False,
        )
        LOGGER.info(
            "HTTP %s; %.3fs",
            response.status_code,
            response.elapsed.total_seconds(),
        )
        if expected_status is not None:
            self.check_status(response, expected_status)
        return response

    @staticmethod
    def check_status(response, expected_status):
        assert response.status_code == expected_status, (
            f"Expected HTTP {expected_status}, got {response.status_code}; "
            f"{response.request.method} {response.request.url}"
        )
