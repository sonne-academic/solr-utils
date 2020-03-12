from solr.configsets import get_config
from solr.instances import get_localhost_session
from data_config import DATA_HOME
from solr.session import SolrSession

CITIES_CSV = DATA_HOME / 'geonames' / 'cities1000.txt'

COLLECTION = 'geotaggerNoAscii'


def make_collection(session: SolrSession):
    session.admin.configs.upload(COLLECTION, get_config(COLLECTION))
    session.admin.collections.create(COLLECTION, 1, 1, 1, COLLECTION)


def send_data(session: SolrSession):
    field_names = [
        'id', 'name', 'ascii_name', 'alternative_names',
        'latitude', 'longitude',
        'feature_class', 'feature_code',
        'country_code', 'cc2',
        'admin1', 'admin2', 'admin3', 'admin4',
        'population', 'elevation', 'dem',
        'timezone', 'modification_date'
    ]
    update_params = {
        'maxSegments': 1,
        'separator': '\t',  # %09
        'encapsulator': '\u0000',  # %00
        'f.alternative_names.split': 'true',
        'f.alternative_names.separator': ','
    }
    session.collection(COLLECTION).update.csv(CITIES_CSV,field_names,commit=True, optimize=True, extra_params=update_params)


def main():
    session = get_localhost_session()
    make_collection(session)
    send_data(session)

if __name__ == '__main__':
    main()


"""
podman run --publish=127.0.0.1:8983:8983 -e SOLR_MODE='solrcloud' -e SOLR_OPTS="-Denable.packages=true -Denable.runtime.lib=true" --name=solr --rm solr

curl -XPOST --data-binary @cities1000.txt \
 -H 'Content-type:application/csv'  \
 'http://localhost:8983/solr/geotagger/update?commit=true&optimize=true&maxSegments=1&separator=%09&encapsulator=%00&fieldnames=id,name,ascii_name,alternative_names,latitude,longitude,feature_class,feature_code,country_code,cc2,admin1,admin2,admin3,admin4,population,elevation,dem,timezone,modification_date&f.alternative_names.split=true&f.alternative_names.separator=,'
 
"""
