from neo4j import GraphDatabase, Record
from typing import Dict, List, Tuple
from .models import Person, Organization


class Neo4jConn:
    def __init__(self, url: str, login: str, password: str):
        # self.driver = GraphDatabase.driver(url, auth=(login, password), encrypted=False)
        self.driver = GraphDatabase.driver(url, encrypted=False)
        self.session = self.driver.session()

    def create_person(self, person: Person) -> Person:
        """
        Create person from @param person
        @param person: model Person
        @type person: Person
        @return: newly created person
        @rtype: Person
        """
        self.session.write_transaction(self._create_person, person)
        return person

    def create_organization(self, organization: Organization) -> Organization:
        """

        @param organization: create model Organization
        @type organization: Organization
        @return: newly created organization
        @rtype: Organization
        """
        self.session.write_transaction(self._create_organization, organization)
        return organization

    def update_person(self, person: Person) -> Person:
        """
        Update person using person.id
        @param person: update model with params from person by using person.id
        @type person: Person
        @return: updated person
        @rtype: Person
        """
        self.session.write_transaction(self._update_person, person)
        return person
        
    def create_membership(self, _id: str, _group_id: str) -> Tuple[str, int]:
        """
        Create relation between person using _id and organization using _group_id
        @param _id: id of the person
        @type _id: str
        @param _group_id: group id of the organization
        @type _group_id: str
        @return: response to request and status code
        @rtype: Tuple[str, int]
        """
        if self.session.read_transaction(self._get_person_organization, _id):
            return 'Person is already MEMBER_OF another org', 409
        return self.session.write_transaction(self._create_membership, _id, _group_id)

    def delete_membership(self, _id: str) -> Tuple[str, int]:
        """
        Delete relation between person using _id and parent of person
        @param _id: id of the person
        @type _id: str
        @return: response to the request and status code
        @rtype: Tuple[str, int]
        """
        return self.session.write_transaction(self._delete_membership, _id)

    def update_organization(self, organization: Organization) -> Organization:
        """
        Update organization using organization.group_id
        @param organization: update model with params from organization by using organization.group_id
        @type organization: Organization
        @return: updated organization
        @rtype: Organization
        """
        self.session.write_transaction(self._update_organization, organization)
        return organization

    def get_person_organization(self, _id: str) -> List[any]:
        """
        Get organization that person is MEMBER_OF using _id
        @param _id: person.id
        @type _id: str
        @return: list that contains organization
        @rtype: List[any]
        """
        return self.session.read_transaction(self._get_person_organization, _id)

    def get_organization_person(self, _group_id) -> List[any]:
        """
        Get all person that are MEMBER_OF organization
        @param _group_id: organization.group_id
        @type _group_id: str
        @return: list that contains person of organization
        @rtype: List[any]
        """
        return self.session.read_transaction(self._get_organization_person, _group_id)

    def delete_person(self, _id: str) -> None:
        """
        Delete person using _id
        @param _id: person.id
        @type _id: str
        @return: no need to return anything
        @rtype: None
        """
        self.session.write_transaction(self._delete_person, _id)

    def delete_organization(self, _group_id: str) -> None:
        """
        Delete organization using _group_id
        @param _group_id: organization.group_id
        @type _group_id: str
        @return: no need to return anything
        @rtype: None
        """
        self.session.write_transaction(self._delete_organization, _group_id)
        
    def build(
            self, people: Dict[str, Person],
            organization: Dict[str, Organization],
            memberships: Dict[str, str],
    ) -> None:
        print('create data')
        self.session.write_transaction(self._create_multiple_people, people)
        self.session.write_transaction(self._create_multiple_organizations, organization)
        self.session.write_transaction(self._create_multiple_memberships, memberships)

    @staticmethod
    def _create_person(tx, person: Person) -> None:
        tx.run(
            'CREATE (p: Person {'
            'id: $id, name: $name, alias: $alias, email: $email, nationality: $nationality'
            '}) RETURN p',
            id=person.id, name=person.name,
            email=person.email, alias=person.alias,
            nationality=person.nationality
        )

    @staticmethod
    def _create_organization(tx, organization: Organization) -> None:
        tx.run(
            'CREATE (o: Organization {'
            'group_id: $group_id, name: $name'
            '}) RETURN o',
            group_id=organization.group_id, name=organization.name,
        )

    @staticmethod
    def _create_membership(tx, _id: str, _group_id: str) -> Tuple[str, int]:
        tx.run(
            'MATCH (p: Person {id: $id}), (o: Organization {group_id: $group_id}) '
            'CREATE (p) - [:MEMBER_OF] -> (o)', id=_id, group_id=_group_id
        )
        return 'Membership created', 201

    @staticmethod
    def _delete_membership(tx, _id: str) -> Tuple[str, int]:
        tx.run(
            'MATCH (:Person {id: $id}) - [m:MEMBER_OF] -> (:Organization) DETACH delete m', id=_id
        )
        return 'Relation deleted', 200

    @staticmethod
    def _update_person(tx, person: Person) -> None:
        tx.run(
            'MATCH (p: Person {id: $id}) '
            'SET p = {id: $id, name: $name, alias: $alias, email: $email, nationality: $nationality} '
            'RETURN p',
            id=person.id, name=person.name,
            email=person.email, alias=person.alias,
            nationality=person.nationality
        )

    @staticmethod
    def _update_organization(tx, organization: Organization) -> None:
        tx.run(
            'MATCH (o: Organization {group_id: $group_id}) '
            'SET o = {group_id: $group_id, name: $name} '
            'RETURN o',
            group_id=organization.group_id, name=organization.name,
        )

    @staticmethod
    def _delete_person(tx, _id: str) -> None:
        tx.run(
            'MATCH (p: Person {id: $id}) DETACH DELETE p', id=_id
        )

    @staticmethod
    def _delete_organization(tx, _group_id: str) -> None:
        tx.run(
            'MATCH (p: Organization {group_id: $group_id}) DETACH DELETE p', group_id=_group_id
        )

    @staticmethod
    def _create_multiple_people(tx, people: Dict[str, Person]) -> None:
        for key in people:
            person = people[key]
            res = tx.run(
                'CREATE (p: Person {'
                'id: $id, name: $name, alias: $alias, email: $email, nationality: $nationality'
                '}) RETURN p',
                id=person.id, name=person.name,
                email=person.email, alias=person.alias,
                nationality=person.nationality
            )
            print('neo4j create', person.name)

    @staticmethod
    def _create_multiple_organizations(tx, organizations: Dict[str, Organization]) -> None:
        for key in organizations:
            organization = organizations[key]
            res = tx.run(
                'CREATE (o: Organization {'
                'group_id: $group_id, name: $name'
                '}) RETURN o',
                group_id=organization.group_id, name=organization.name,
            )
            print('neo4j create', organization.name)

    @staticmethod
    def _create_multiple_memberships(tx, memberships: Dict[str, str]) -> None:
        for key in memberships:
            group_id = memberships[key]
            tx.run(
                "MATCH (p: Person {id: $id})"
                "MATCH (o: Organization {group_id: $group_id})"
                "MERGE (p)-[Memberships:MEMBER_OF]->(o)",
                id=key, group_id=group_id
            )

    @staticmethod
    def _get_person_organization(tx, _id: str) -> List[any]:
        res = tx.run(
            'MATCH (p: Person {id: $id}) - [:MEMBER_OF] -> (o: Organization) return o', id=_id
        )
        res = [record for record in res.data()]
        return [
            Organization(db_dict=record['o']).__dict__ for record in res if 'o' in record
        ]

    @staticmethod
    def _get_organization_person(tx, _group_id: str) -> List[any]:
        res = tx.run(
            'MATCH (p: Person) - [:MEMBER_OF] -> (o: Organization {group_id: $group_id}) return p',
            group_id=_group_id
        )
        res = [record for record in res.data()]
        return [
            Person(db_dict=record['p']).__dict__ for record in res if 'p' in record
        ]

    def close(self):
        self.driver.close()

