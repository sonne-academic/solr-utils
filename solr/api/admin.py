from solr.api import SolrPathApi
from pathlib import Path
import io
import zipfile


__all__ = ['SolrAdmin']


class SolrAdmin:
    def __init__(self, session):
        self.session = session
        self._configs = Configs(session)
        self._collections = Collections(session)

    @property
    def configs(self):
        return self._configs

    @property
    def collections(self):
        return self._collections


def build_config_zip(path: Path) -> io.BytesIO:
    if not path.exists():
        raise KeyError('path does not exist')
    if not path.is_dir():
        raise KeyError('path is not a directory')

    dirs = [path]
    bio = io.BytesIO()

    with zipfile.ZipFile(bio, mode='w') as zipf:
        for dir in dirs:
            for thing in dir.iterdir():
                if thing.is_dir():
                    dirs.append(thing)
                    zipf.writestr(str(thing.relative_to(path))+'/','')
                else:
                    zipf.write(thing,thing.relative_to(path))

    return bio


class Configs(SolrPathApi):
    def __init__(self, session):
        super().__init__(session, 'admin/configs')

    def list(self):
        params = {'action': 'LIST'}
        return self._get(params=params)

    def delete(self, name):
        params = {'action': 'DELETE', 'name': name}
        return self._get(params=params)

    def create(self, name: str, baseConfigSet: str, configSetProps: dict = None):
        params = {
            'action': 'CREATE',
            'name': name,
            'baseConfigSet': baseConfigSet
        }
        if None is not configSetProps:
            # e.g. configSetProp.immutable=false
            for k, v in configSetProps.items():
                params[f'configSetProp.{k}'] = v

        return self._get(params=params)

    def upload(self, name, configPath: Path):
        params = {'action': 'UPLOAD', 'name': name}
        headers = {'Content-Type': 'application/octet-stream'}
        zipcontent = build_config_zip(configPath)

        return self._post(headers=headers, params=params, data=zipcontent.getbuffer())


class Collections(SolrPathApi):
    def __init__(self, session):
        super().__init__(session, 'admin/collections')

    def create(self, name, num_shards, replication_factor, max_shards_per_node, config_name):
        #  property.name=value instead of core.properties file.
        params = {
            'action': 'CREATE',
            'name': name,
            'numShards': num_shards,
            'replicationFactor': replication_factor,
            'maxShardsPerNode': max_shards_per_node,
            'collection.configName': config_name
        }
        return self._get(params=params)

    def delete(self, name):
        params = {
            'action': 'DELETE',
            'name': name,
        }
        return self._get(params=params)

    def reload(self, name):
        params = {
            'action': 'RELOAD',
            'name': name,
        }
        return self._get(params=params)

    def migrate(self):
        raise NotImplementedError

    def clusterstatus(self):
        params = {
            'action': 'CLUSTERSTATUS'
        }
        return self._get(params=params)

    def requeststatus(self, request_id):
        params = {
            'action': 'REQUESTSTATUS',
            'requestid': request_id
        }
        return self._get(params=params)

    def deletestatus(self, request_id):
        params = {
            'action': 'DELETESTATUS',
            'requestid': request_id
        }
        return self._get(params=params)

    def list(self):
        params = {
            'action': 'LIST'
        }
        # response = self._get(params=params)
        # data = response.json()
        # return data['collections']
        return self._get(params=params)

    def createalias(self, alias_name, collections: list):
        params = {
            'action': 'CREATEALIAS',
            'name': alias_name,
            'collections': ','.join(collections)
        }
        return self._get(params=params)

    def deletealias(self, alias_name):
        params = {
            'action': 'DELETEALIAS',
            'name': alias_name,
        }
        return self._get(params=params)

    def listaliases(self):
        params = {
            'action': 'LISTALIASES'
        }
        return self._get(params=params)

    def aliasprop(self, alias_name, props):
        params = {
            'action': 'ALIASPROP',
            'name': alias_name,
        }
        return self._get(params=params)


