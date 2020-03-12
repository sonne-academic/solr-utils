from solr.api import SolrPathApi


class SolrCollectionSchema(SolrPathApi):
    def __init__(self, session, collection_name: str):
        super().__init__(session, collection_name + '/schema')
        self._fields = SolrField(session, collection_name)
        self._field_types = SolrFieldType(session, collection_name)
        self._copy_fields = SolrCopyField(session, collection_name)
        self._dynamic_fields = SolrDynamicField(session, collection_name)

    @property
    def fields(self):
        return self._fields

    @property
    def field_types(self):
        return self._field_types

    @property
    def copy_fields(self):
        return self._copy_fields

    @property
    def dynamic_fields(self):
        return self._dynamic_fields


class SolrFieldType(SolrPathApi):
    def __init__(self, session, collection_name: str):
        super().__init__(session, collection_name + '/schema/fieldtypes')
        self.collection = collection_name

    def command(self, command, params):
        return self.session._post_path(f'{self.collection}/schema', json={command: params})

    def get_all(self, show_defaults=False):
        if show_defaults:
            params = {'showDefaults': 'true'}
        else:
            params = {'showDefaults': 'false'}
        return self._get(params=params)

    def get_single(self, name):
        return self.session._get_path(self.path + f'/{name}')

    def add(self, name, java_class, **props):
        params = {
            'name': name,
            'class': java_class,
        }
        params.update(props)
        return self.command('add-field-type', params)

    def delete(self, name):
        params = {'name': name}
        return self.command('delete-field-type', params)

    def replace(self, name, cls, **props):
        params = {
            'name': name,
            'class': cls,
        }
        params.update(props)
        return self.command('replace-field-type', params)


class SolrField(SolrPathApi):
    def __init__(self, session, collection_name: str):
        super().__init__(session, collection_name + '/schema/fields')
        self.collection = collection_name

    def command(self, command, params):
        return self.session._post_path(f'{self.collection}/schema', json={command: params})

    def get_all(self, show_defaults=False):
        if show_defaults:
            params = {'showDefaults': 'true'}
        else:
            params = {'showDefaults': 'false'}
        return self._get(params=params)

    def get_single(self, name):
        return self.session._get_path(self.path + f'/{name}')

    def add(self, name, type, **props):
        params = {
            'name': name,
            'type': type,
        }
        params.update(props)
        return self.command('add-field', params)

    def delete(self, name):
        params = {'name': name}
        return self.command('delete-field', params)

    def replace(self, name, type, **props):
        params = {
            'name': name,
            'type': type,
        }
        params.update(props)
        return self.command('replace-field', params)


class SolrDynamicField(SolrPathApi):
    def __init__(self, session, collection_name: str):
        super().__init__(session, collection_name + '/schema/dynamicfields')
        self.collection = collection_name

    def command(self, command, params):
        return self.session._post_path(f'{self.collection}/schema', json={command: params})

    def get_all(self, show_defaults=False):
        if show_defaults:
            params = {'showDefaults': 'true'}
        else:
            params = {'showDefaults': 'false'}

        return self._get(params=params)

    def get_single(self, name):
        return self.session._get_path(self.path + f'/{name}')

    def add(self, name, type, **props):
        params = {
            'name': name,
            'type': type,
        }
        params.update(props)
        return self.command('add-dynamic-field', params)

    def delete(self, name):
        params = {'name': name}
        return self.command('delete-dynamic-field', params)

    def replace(self, name, type, **props):
        params = {
            'name': name,
            'class': type,
        }
        params.update(props)
        return self.command('replace-dynamic-field', params)


class SolrCopyField(SolrPathApi):
    def __init__(self, session, collection_name: str):
        super().__init__(session, collection_name + '/schema/copyfields')
        self.collection = collection_name

    def command(self, command, params):
        return self.session._post_path(f'{self.collection}/schema', json={command: params})

    def get_all(self):
        return self._get()

    def get_by_source(self, source_field_name):
        params = {'source.fl': source_field_name}
        return self._get(params=params)

    def get_by_dest(self, dest_field_name):
        params = {'dest.fl': dest_field_name}
        return self._get(params=params)

    def get_single(self, name):
        return self.session._get_path(self.path + f'/{name}')

    def add(self, source, dest, max_chars=None):
        params = {
            'source': source,
            'dest': dest,
        }
        if None is not max_chars:
            params['maxChars'] = max_chars
        return self.command('add-copy-field', params)

    def delete(self, source, dest):
        params = {
            'source': source,
            'dest': dest,
        }
        return self.command('delete-copy-field', params)

    def replace(self, name, type, **props):
        params = {
            'name': name,
            'class': type,
        }
        params.update(props)
        return self.command('replace-copy-field', params)

