# from sshtunnel import SSHTunnelForwarder
from solr.session import SolrConnector, SolrSession, SolrAsyncSession


class LocalhostConnector(SolrConnector):
    def __init__(self, port: int):
        self.port = port

    def connect(self) -> str:
        return f'http://localhost:{self.port}/solr/'

    def close(self):
        pass


class HostConnector(SolrConnector):
    def __init__(self, host: str, port: int):
        self.port = port
        self.host = host

    def connect(self) -> str:
        return f'http://{self.host}:{self.port}/solr/'

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


class SolrKubernetesConnector(SolrConnector):
    def __init__(self,
                 host='127.0.0.1',
                 kubernetes_port=8001,
                 namespace='default',
                 service_name='solr-service',
                 service_port=8983):
        self.url = f'http://{host}:{kubernetes_port}/api/v1/namespaces/{namespace}'
        self.url += f'/services/http:{service_name}:{service_port}/proxy/solr/'

    def connect(self) -> str:
        return self.url

    def close(self):
        pass


def get_production_session():
    return SolrSession(SolrJumpHostConnector('cloud', 'solr0', 'arch'))


def get_develop_session():
    return SolrSession(SolrJumpHostConnector('mk4', 'solr', 'bone', 6))


def get_localhost_session(port=8983):
    return SolrSession(LocalhostConnector(port))


def get_kubernetes_proxy_session():
    return SolrSession(SolrKubernetesConnector())


def get_session(host='solr0', port=8983):
    return SolrSession(HostConnector(host, port))


def get_async_localhost_session(port=8983):
    return SolrAsyncSession(LocalhostConnector(port))
