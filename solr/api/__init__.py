from requests import Response

class SolrPathApi:
    def __init__(self, session, path: str):
        self.session = session
        self.path = path

    def _post(self, **kwargs) -> Response:
        response = self.session._post_path(self.path, **kwargs)
        return response

    def _get(self, **kwargs) -> Response:
        response = self.session._get_path(self.path, **kwargs)
        return response

    def command(self, path, command, params):
        return self.session._post_path(f'{path}', json={command: params})


