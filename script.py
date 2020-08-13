import os
import csv
from neo4j import GraphDatabase
from typing import Dict


people = {}
organizations = {}
memberships = {}

# read from csv file
def read_csv():
    here = os.path.dirname(os.path.abspath(__file__))

    filename = os.path.join(here, 'gb_parliament.csv')

    return open(filename, newline='')


class Organization:
    def __init__(self, line):
        self.group_id = line[7]
        self.name = line[6]


class Person:
    def __init__(self, line):
        self.id = line[0]
        self.name = line[1]
        self.alias = line[2]
        self.email = line[3]
        self.nationality = 'GB'
        

    def __repr__(self):
        return f'{self.alias} with id={self.id}'

class Connection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_people(self, people: Dict[str, Person]) -> None:
        with self.driver.session() as session:
            # merge each person into db
            for key in people:
                person_id = session.write_transaction(self._create_and_return_person, people[key])
                print(person_id)

    def create_organizations(self, organizations: Dict[str, Organization]) -> None:
        with self.driver.session() as session:
            # merge each organization into db
            for key in organizations:
                organization_id = session.write_transaction(self._create_and_return_organization, organizations[key])
                print(organization_id)

    def create_memberships(self, memberships: Dict[str, str]) -> None:
        with self.driver.session() as session:
            # join all people and organizations
            for key in memberships:
                session.write_transaction(self._create_and_return_membership, key, memberships[key])
                print(f'join {key} and {memberships[key]}')

    @staticmethod
    def _create_and_return_person(tx, person: Person) -> int:
        result = tx.run("Merge (p:Person {id: $id, name: $name, alias: $alias, email: $email, nationality: $nationality}) "
                    "RETURN id(p) AS node_id", id=person.id, name=person.name, alias=person.alias, email=person.email, nationality=person.nationality)
        return result.single()[0]

    @staticmethod
    def _create_and_return_organization(tx, organization: Organization) -> int:
        result = tx.run("Merge (o:Organization {group_id: $group_id, name: $name}) "
                    "RETURN id(o) AS node_id", group_id=organization.group_id, name=organization.name)
        return result.single()[0]

    @staticmethod
    def _create_and_return_membership(tx, id: str, group_id: str) -> None:
        result = tx.run("MATCH (p: Person {id: $id})"
                        "MATCH (o: Organization {group_id: $group_id})"
                        "MERGE (p)-[membership:MEMBER_OF]->(o)", id=id, group_id=group_id)
        return True



# read csv file
f = read_csv()

# get all lines from csv file
lines = csv.reader(f, delimiter=',', quotechar='"')

# iterate each line from csv except 1st that holds headers
for i, line in enumerate(lines):
    if i:
        # get person
        person = Person(line)

        # get organization
        organization = Organization(line) 

         # save data to dictionary
        people[person.id] = person
        organizations[organization.group_id] = organization
        memberships[person.id] = organization.group_id


# initialize connection to neo4j
conn = Connection('bolt://localhost:7687', 'neo4j', 'test')

print(len(people), len(organizations))

# create nodes
conn.create_people(people)
conn.create_organizations(organizations)

# create relation
conn.create_memberships(memberships)

conn.close()
