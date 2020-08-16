from neo4j import GraphDatabase
from typing import Dict, List
from .models import Person, Organization


class Neo4jConn:
    def __init__(self, url: str, login: str, password: str):
        self.driver = GraphDatabase.driver(url, auth=(login, password), encrypted=False)
        print('load neo4j successfully')
        self.session = self.driver.session()

    def build(
            self, people: Dict[str, Person],
            organization: Dict[str, Organization], memberships: Dict[str, str],
    ) -> None:
        print('create data')
        self.session.write_transaction(self._create_multiple_people, people)
        self.session.write_transaction(self._create_multiple_organizations, organization)
        self.session.write_transaction(self._create_multiple_memberships, memberships)

    @staticmethod
    def _create_multiple_people(tx, people: Dict[str, Person]) -> None:
        for key in people:
            person = people[key]
            res = tx.run(
                'MERGE (p: Person {'
                'id: $id, name: $name, alias: $alias, email: $email, nationality: $nationality'
                '}) return p',
                id=person.id, name=person.name,
                email=person.email, alias=person.alias,
                nationality=person.nationality
            )
            print([record.value() for record in res])

    @staticmethod
    def _create_multiple_organizations(tx, organizations: Dict[str, Organization]) -> None:
        for key in organizations:
            organization = organizations[key]
            res = tx.run(
                'MERGE (o: Organization {'
                'group_id: $group_id, name: $name'
                '}) return o',
                group_id=organization.group_id, name=organization.name,
            )
            print([record.value() for record in res])

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
    def _is_empty_db(tx) -> int:
        res = tx.run('MATCH (n) return count(n)')
        return [record.value() for record in res][0]

    def close(self):
        self.driver.close()

