import json
import requests
from typing import Dict
from .entity import Person, Organization


class ElasticsearchConnection:
    def __init__(self, _index: str):
        self.url = 'http://localhost:9200/' + _index + '/'
        self.routing = '?routing=1&refresh'

    def create_nodes(
            self, _people: Dict[str, Person],
            _organizations: Dict[str, Organization], _memberships: Dict[str, str]
    ) -> None:
        # create nodes
        self.create_organizations(_organizations)
        self.create_people(_people, _memberships)

    def create_people(self, _people: Dict[str, Person], _memberships: Dict[str, str]):
        for i in _people:
            data = {
                "person": {
                    "id": i,
                    "name": _people[i].name,
                    "alias": _people[i].alias,
                    "email": _people[i].email,
                    "nationality": _people[i].nationality
                },
                "memberships": {
                    "name": "person",
                    "parent": _memberships[i]
                }
            }

            response = self._elasticsearch_curl(
                self.url + '_doc/' + i + self.routing,
                method='put', body=json.dumps(data)
            )

    def create_organizations(self, _organizations: Dict[str, Organization]) -> None:
        for i in _organizations:
            data = {
                "organization": {
                    "group_id": i,
                    "name": _organizations[i].name,
                }
            }

            response = self._elasticsearch_curl(
                self.url + '_doc/' + i + self.routing,
                method='put', body=json.dumps(data)
            )

    def _generate_mapping(self):
        body = {
            "mappings": {
                "properties": {
                    "person": {
                        "properties": {
                            "id": {"type": "keyword"},
                            "name": {"type": "text"},
                            "password": {"type": "text"}
                        }
                    },
                    "organization": {
                        "properties": {
                            "group_id": {"type": "keyword"},
                            "name": {"type": "text"},
                        },
                    },
                    "memberships": {
                        "type": "join",
                        "relations": {
                            "organization": "person"
                        }
                    }
                }
            }
        }

        self._elasticsearch_curl(self.url, method='put', body=json.dumps(body))

    @staticmethod
    def _elasticsearch_curl(uri: str, method='get', body='') -> str:
        headers = {
            'Content-Type': 'application/json',
        }

        try:
            # make HTTP verb parameter case-insensitive by converting to lower()
            if method.lower() == "get":
                response = requests.get(uri, headers=headers, data=body)
            elif method.lower() == "post":
                response = requests.post(uri, headers=headers, data=body)
            elif method.lower() == "put":
                response = requests.put(uri, headers=headers, data=body)

            # read the text object string
            try:
                resp_text = json.loads(response.text)
            except:
                resp_text = response.text

            # catch exceptions and print errors to terminal
        except Exception as error:
            print('\nelasticsearch_curl() error:', error)
            resp_text = error

        # return the Python dict of the request
        return resp_text
