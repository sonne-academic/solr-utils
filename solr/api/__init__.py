from requests import Response

class SolrPathApi:
    def __init__(self, session, path: str):
        self.session = session
        self.path = path

    def _post(self, **kwargs) -> Response:
        return self.session._post_path(self.path, **kwargs)

    def _get(self, **kwargs) -> Response:
        return self.session._get_path(self.path, **kwargs)


