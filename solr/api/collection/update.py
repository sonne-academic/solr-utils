from typing import List, Dict, Any, Iterable, Optional

from solr.api import SolrPathApi
from pathlib import Path


def bool_helper(value: bool) -> str:
    if value:
        return 'true'
    return 'false'


class SolrCollectionUpdate(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/update')

    def _raw_update(self, content_type: str, data: Iterable, commit: bool, optimize: bool,
                    commit_within: Optional[int] = None, overwrite: Optional[bool] = None,
                    expunge_deletes: Optional[bool] = None, max_segments: Optional[int] = None,
                    wait_searcher: Optional[bool] = None):
        headers = {'Content-Type': content_type}
        params = {
            'commit': bool_helper(commit),
            'optimize': bool_helper(optimize),
        }
        if None is not commit_within:
            params['commitWithin'] = commit_within
        if None is not overwrite:
            params['overwrite'] = bool_helper(overwrite)
        if None is not expunge_deletes:
            params['expungeDeletes'] = bool_helper(expunge_deletes)
        if None is not max_segments:
            params['maxSegments'] = max_segments
        return self._post(headers=headers, data=data, params=params)

    def xml(self, iterable):
        headers = {'Content-Type': 'text/xml'}
        return self._post(headers=headers, data=iterable)

    def jsonl(self, iterable, commit=True):
        headers = {'Content-Type': 'application/json'}
        if commit:
            params = {
                'commit': 'true'
            }
        else:
            params = {
                'commit': 'false'
            }
        return self.session._post_path(self.path + '/json/docs', headers=headers, params=params, data=iterable)

    def jsonUpdate(self, iterable, commit=True):
        headers = {'Content-Type': 'application/json'}
        if commit:
            params = {
                'commit': 'true'
            }
        else:
            params = {
                'commit': 'false'
            }
        return self.session._post_path(self.path, headers=headers, params=params, data=iterable)

    def csv(self, csv_path: Path, field_names: List[str], commit: bool = True, optimize: bool = False,
            extra_params: Dict[str, Any] = None):
        params = {
            'commit': bool_helper(commit),
            'optimize': bool_helper(optimize),
            'fieldnames': ','.join(field_names)
        }
        params.update(extra_params)

        return self.session._post_path(self.path + '/csv', params=params, data=csv_path.read_bytes())
