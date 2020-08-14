from neo4j import GraphDatabase
from typing import Dict
from .entity import Person, Organization


class Neo4jConnection:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_nodes(
            self, _people: Dict[str, Person],
            _organizations: Dict[str, Organization], _memberships: Dict[str, str]
    ) -> None:
        # create nodes
        self.create_people(_people)
        self.create_organizations(_organizations)
        # create relation
        self.create_memberships(_memberships)

    def create_people(self, _people: Dict[str, Person]) -> None:
        with self.driver.session() as session:
            # merge each person into db
            for key in _people:
                person_id = session.write_transaction(self._create_and_return_person, _people[key])
                # print(person_id)

    def create_organizations(self, _organizations: Dict[str, Organization]) -> None:
        with self.driver.session() as session:
            # merge each organization into db
            for key in _organizations:
                organization_id = session.write_transaction(self._create_and_return_organization, _organizations[key])
                # print(organization_id)

    def create_memberships(self, _memberships: Dict[str, str]) -> None:
        with self.driver.session() as session:
            # join all people and organizations
            for key in _memberships:
                session.write_transaction(self._create_and_return_membership, key, _memberships[key])
                # print(f'join {key} and {_memberships[key]}')

    @staticmethod
    def _create_and_return_person(tx, _person: Person) -> int:
        result = tx.run(
            "Merge (p:Person {id: $id, name: $name, alias: $alias, email: $email, nationality: $nationality}) "
            "RETURN id(p) AS node_id",
            id=_person.id,
            name=_person.name,
            alias=_person.alias,
            email=_person.email,
            nationality=_person.nationality
        )
        return result.single()[0]

    @staticmethod
    def _create_and_return_organization(tx, _organization: Organization) -> int:
        result = tx.run(
            "Merge (o:Organization {group_id: $group_id, name: $name}) "
            "RETURN id(o) AS node_id",
            group_id=_organization.group_id,
            name=_organization.name
        )
        return result.single()[0]

    @staticmethod
    def _create_and_return_membership(tx, _id: str, _group_id: str) -> bool:
        tx.run(
            "MATCH (p: Person {id: $id})"
            "MATCH (o: Organization {group_id: $group_id})"
            "MERGE (p)-[Memberships:MEMBER_OF]->(o)",
            id=_id,
            group_id=_group_id
        )
        return True
