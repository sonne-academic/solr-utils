from sshtunnel import SSHTunnelForwarder
from solr.session import SolrConnector, SolrSession, SolrAsyncSession


class LocalhostConnector(SolrConnector):
    def __init__(self, port: int):
        self.port = port

    def connect(self) -> str:
        return f'http://localhost:{self.port}/solr/'

    def close(self):
        pass


class SolrJumpHostConnector(SolrConnector):
    def __init__(self, jump_host, private_host, user, ssh_port=22, solr_port=8983, local_port=0):
        self.tunnel = SSHTunnelForwarder(
            (jump_host, ssh_port),
            ssh_username=user,
            remote_bind_address=(private_host, solr_port),
            local_bind_address=('127.0.0.1', local_port)
        )

    def connect(self) -> str:
        self.tunnel.start()
        ip, port = self.tunnel.local_bind_address
        return f'http://{ip}:{port}/solr/'

    def close(self):
        self.tunnel.stop()


def get_production_session():
    return SolrSession(SolrJumpHostConnector('cloud', 'solr0', 'arch'))


def get_develop_session():
    return SolrSession(SolrJumpHostConnector('mk4', 'solr', 'bone', 6))


def get_localhost_session(port=8983):
    return SolrSession(LocalhostConnector(port))


def get_async_localhost_session(port=8983):
    return SolrAsyncSession(LocalhostConnector(port))
