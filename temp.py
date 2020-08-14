import json
data = {
    "query": {
        "parent_id": {
            "type": "person",
            "id": "11"
        }
    }
}

# elasticsearch_curl(url + '_search', verb='get', json_body=json.dumps(data))

data = {
    "query": {
        "child_id": {
            "type": "organisation",
            "id": "3"
        }
    }
}
