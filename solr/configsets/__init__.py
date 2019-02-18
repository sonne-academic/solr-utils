"""
upload configset with:
(cd server/solr/configsets/sample_techproducts_configs/conf && zip -r - *) | curl -X POST --header "Content-Type:application/octet-stream" --data-binary @- "http://localhost:8983/solr/admin/configs?action=UPLOAD&name=myConfigSet"
"""