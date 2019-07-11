"""
upload configset with:
(cd server/solr/configsets/sample_techproducts_configs/conf && zip -r - *) | curl -X POST --header "Content-Type:application/octet-stream" --data-binary @- "http://localhost:8983/solr/admin/configs?action=UPLOAD&name=myConfigSet"
"""
from pathlib import Path

module_path = Path(__file__).parent
cfg_path = module_path / 'configs'


def get_config(name: str):
    return cfg_path / name
