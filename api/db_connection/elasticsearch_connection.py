from elasticsearch import Elasticsearch
from typing import Dict
from . import settings

from .models import Person, Organization


class ElasticsearchConn:
    def __init__(self, index):
        self.es = None
        self.index = index
        while True:
            try:
                self.es = Elasticsearch(hosts=[f'http://{settings.ES_HOST}:{settings.ES_PORT}'])
                if not self.es.ping():
                    print('Connection error')
                    break
                else:
                    print('load es successfully')
                    break
            except Exception as e:
                pass

    def build(self, people: Dict[str, Person], organizations: Dict[str, Organization]) -> bool:
        print('build models in es')
        if not self.es.indices.exists(index=self.index):
            self._create_people(people)
            self._create_organizations(organizations)
            return False
        return False

    def _create_people(self, people: Dict[str, Person]):
        print('create_people in ', self.index)
        pass

    def _create_organizations(self, organizations: Dict[str, Organization]):
        print('create organizations in ', self.index)
        pass
