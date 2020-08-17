from neo4j import GraphDatabase
from typing import Dict, List
from .models import Person, Organization


class Neo4jConn:
    def __init__(self, url: str, login: str, password: str):
        self.driver = GraphDatabase.driver(url, auth=(login, password), encrypted=False)
        self.session = self.driver.session()

    def create_person(self, person: Person) -> None:
        self.session.write_transaction(self._create_person, person)

    def create_organization(self, organization: Organization) -> None:
        self.session.write_transaction(self._create_organization, organization)

    def update_person(self, person: Person) -> None:
        self.session.write_transaction(self._update_person, person)

    def update_organization(self, organization: Organization) -> None:
        self.session.write_transaction(self._update_organization, organization)

    def get_person_organization(self, _id):
        pass

    def get_organization_person(self, _group_id):
        pass

    def delete_person(self, _id: str) -> None:
        self.session.write_transaction(self._delete_person, _id)

    def delete_organization(self, _group_id: str) -> None:
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
        pass

    @staticmethod
    def _get_organization_person(tx, _group_id: str) -> List[any]:
        pass

    def close(self):
        self.driver.close()

