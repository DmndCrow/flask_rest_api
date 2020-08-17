import csv
from typing import Dict

from .neo4j_connection import Neo4jConn
from .elasticsearch_connection import ElasticsearchConn
from .models import Person, Organization
from . import settings

import os
import sys


def get_csv_data() -> tuple:
    """
    Function that loads data from csv and stores it in dictionaries
    """
    _people = {}
    _organizations = {}
    _memberships = {}

    # read csv file
    f = open(os.path.join(os.path.dirname(sys.argv[0]), 'db_connection/gb_parliament.csv'), 'r', newline='')

    # get all lines from csv file
    lines = csv.reader(f, delimiter=',', quotechar='"')

    # iterate each line from csv except 1st that holds headers
    for i, line in enumerate(lines):
        if i:
            # get person
            person = Person(csv_list=line)

            # get organization
            organization = Organization(csv_list=line)

            # save data to dictionary
            _people[person.id] = person
            _organizations[organization.group_id] = organization
            _memberships[person.id] = organization.group_id

    return _people, _organizations, _memberships


def upload_to_neo4j(
        _people: Dict[str, Person],
        _organizations: Dict[str, Organization],
        _memberships: Dict[str, str],
) -> None:
    """
    Function takes dictionaries and upload data to neo4j db
    """

    # initialize connection to neo4j
    conn = Neo4jConn(
        url=f'neo4j://{settings.NEO4J_HOST}:{settings.NEO4J_PORT}',
        login=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )

    # generate nodes
    conn.build(_people, _organizations, _memberships)

    # close connection
    conn.close()


def upload_to_elasticsearch(
        _people: Dict[str, Person],
        _organizations: Dict[str, Organization]
) -> bool:
    """
    Function takes dictionaries and upload data to Elasticsearch db
    """
    # initialize connection to Elasticsearch
    print('init es')
    conn = ElasticsearchConn(host=settings.ES_HOST, port=settings.ES_PORT)

    # generate nodes
    print('build es')
    return conn.build(_people, _organizations)


def upload_data():
    # store data from csv file in dictionaries
    people, organizations, memberships = get_csv_data()
    # upload data to DBs
    print('upload data es')
    res = upload_to_elasticsearch(people, organizations)
    if res:
        upload_to_neo4j(people, organizations, memberships)





