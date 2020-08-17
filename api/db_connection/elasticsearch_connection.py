import json
import uuid

from elasticsearch import Elasticsearch, helpers
from typing import Dict, List, Tuple

from .models import Person, Organization


class ElasticsearchConn:
    def __init__(self, host, port):
        self.es = None
        self.doc = '_doc'
        # wait for elasticsearch service to start
        while True:
            try:
                self.es = Elasticsearch(hosts=[f'http://{host}:{port}'])
                break
            except Exception as e:
                print(e)

    def get_person_by_id(self, _id: str = None) -> Tuple[List[Dict[str, str]], int]:
        """
        Get person from db by person id, if not provided get all people
        @param _id: person id
        @type _id: str
        @return: list of people
        @rtype: List[Dict[str, str]]
        """
        if _id:
            try:
                res = self.es.get(index='person', doc_type=self.doc, id=_id)
                return [res['_source']], 200
            except:
                return [], 404
        else:
            query = {
                'query': {
                    'match_all': {}
                }
            }
        es_response = helpers.scan(
            self.es,
            index='person',
            doc_type=self.doc,
            query=query
        )
        return [record['_source'] for record in es_response], 200

    def get_organization_by_group_id(self, _group_id: str = None) -> Tuple[List[Dict[str, str]], int]:
        """
        Get organization from db by group id, if not provided get all organizations
        @param _group_id: group od
        @type _group_id: str
        @return: list of organizations
        @rtype: List[Dict[str, str]]
        """
        if _group_id:
            try:
                res = self.es.get(index='organization', doc_type=self.doc, id=_group_id)
                return [res['_source']], 200
            except:
                return [], 404
        else:
            query = {
                'query': {
                    'match_all': {}
                }
            }
        es_response = helpers.scan(
            self.es,
            index='organization',
            doc_type=self.doc,
            query=query
        )
        return [record['_source'] for record in es_response], 200

    def update_person(self, person: Person) -> int:
        """
        Update person by using person
        @param person: all params of the to be updated person
        @type person: Person
        @return: status code
        @rtype: int
        """
        res, code = self.get_person_by_id(person.id)
        if code == 200:
            self.es.update(
                index='person',
                doc_type='_doc',
                id=person.id,
                body={'doc': person.__dict__}
            )
            return 200
        return 404

    def update_organization(self, organization: Organization) -> int:
        """
        Update organization by using organization
        @param organization: all params of the to be updated organization
        @type organization: Organization
        @return: status code
        @rtype: int
        """
        res, code = self.get_organization_by_group_id(organization.group_id)
        if code == 200:
            self.es.update(
                index='organization',
                doc_type='_doc',
                id=organization.group_id,
                body={'doc': organization.__dict__}
            )
            return 200
        return 404

    def delete_person(self, _id: str) -> int:
        """
        Try to delete person using _id
        @param _id: person.id
        @type _id: str
        @return: status code
        @rtype: int
        """
        try:
            self.es.delete(index='person', doc_type=self.doc, id=_id)
            return 200
        except:
            return 404

    def delete_organization(self, _group_id: str) -> int:
        """
        Try to delete organization using _group_id
        @param _group_id: organization.group_id
        @type _group_id: str
        @return: status code
        @rtype: int
        """
        try:
            self.es.delete(index='organization', doc_type=self.doc, id=_group_id)
        except:
            return 404

    def create_person(self, person: Person) -> Person:
        """
        Create new person
        @param person: to be created Person
        @type person: Person
        @return: created person
        @rtype: Person
        """
        index = 'person'
        # make sure id of the to be created person is unique
        while True:
            res, code = self.get_person_by_id(person.id)
            if code == 404:
                break
            else:
                person.id = str(uuid.uuid4())

        self.es.index(
            index=index,
            doc_type=self.doc,
            id=person.id,
            body=person.__dict__
        )

        return person

    def create_organization(self, organization: Organization) -> Organization:
        """
        Create new organization
        @param organization: to be created Organization
        @type organization: Organization
        @return: created organization
        @rtype: Organization
        """
        index = 'organization'
        # make sure id of the to be created organization is unique
        while True:
            res, code = self.get_organization_by_group_id(organization.group_id)

            if code == 404:
                break
            else:
                organization.group_id = str(uuid.uuid4())

        self.es.index(
            index=index,
            doc_type=self.doc,
            id=organization.group_id,
            body=organization.__dict__
        )

        return organization

    def build(self, people: Dict[str, Person], organizations: Dict[str, Organization]) -> bool:
        """
        Create people and organizations in elasticsearch if index doesnt exist.
        Return True to add same data to neo4j db
        """
        if not self.es.indices.exists(index='person') and not self.es.indices.exists(index='organization'):
            self._create_organizations(organizations)
            self._create_people(people)
            return True
        return False

    def _create_people(self, people: Dict[str, Person]) -> None:
        """
        Add each person to db of type Person
        """
        index = 'person'
        print(f'create person in {index}')
        for key in people:
            self.es.index(
                index=index,
                doc_type=self.doc,
                id=key,
                body=people[key].__dict__
            )
            print(f'es create {index}', people[key].name)

    def _create_organizations(self, organizations: Dict[str, Organization]) -> None:
        """
        Add each organization to db of type Organization
        """
        index = 'organization'
        print(f'create organizations in {index}')
        for key in organizations:
            self.es.index(
                index=index,
                doc_type=self.doc,
                id=key,
                body=organizations[key].__dict__
            )
            print(f'es create {index}', organizations[key].name)
