from data.mag import generate_reference_updates
from solr.instances import get_localhost_session
from data import upload_batches_unparsed


def upload(s):
    upload_batches_unparsed(s, 'mag_papers', generate_reference_updates())


if __name__ == '__main__':
    s = get_localhost_session()
    response = s.collection('mag_papers').schema.fields.get_single('References')
    if 200 != response.status_code:
        print('adding field for references:')
        print(s.collection('mag_papers').schema.fields.add('References', 'important_strings').json())
    upload(s)
