import csv
import time
import os

from scripts.entity import Person, Organization
from scripts.neo4j_upload import Neo4jConnection
from scripts.elasticsearch_upload import ElasticsearchConnection


def timing(f):
    """
    Decorator to compute time taken to execute function
    """
    def compute(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()

        print(f'Time taken for {f.__name__} is {end - start} seconds')

        return result

    return compute


def read_csv():
    """
    Function to read data from csv file
    """
    here = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(here, 'gb_parliament.csv')
    return open(filename, newline='')


def load_data_csv() -> tuple:
    """
    Function that loads data from csv and stores it in dictionaries
    """
    _people = {}
    _organizations = {}
    _memberships = {}

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
            _people[person.id] = person
            _organizations[organization.group_id] = organization
            _memberships[person.id] = organization.group_id

    return _people, _organizations, _memberships


@timing
def upload_to_neo4j(_people, _organizations, _memberships) -> None:
    """
    Function takes dictionaries and upload data to neo4j db
    """

    # initialize connection to neo4j
    conn = Neo4jConnection('bolt://localhost:7687', 'neo4j', 'test')

    # generate nodes
    conn.create_nodes(_people, _organizations, _memberships)

    # close connection
    conn.close()


@timing
def upload_to_elasticsearch(_people, _organizations, _memberships) -> None:
    """
    Function takes dictionaries and upload data to Elasticsearch db
    """
    # initialize connection to Elasticsearch
    conn = ElasticsearchConnection('challenge')

    # generate nodes
    conn.create_nodes(people, organizations, memberships)


if __name__ == '__main__':
    # store data from csv file in dictionaries
    people, organizations, memberships = load_data_csv()
    print('Hello world')
    # upload data to DBs
    # upload_to_neo4j(people, organizations, memberships)
    # upload_to_elasticsearch(people, organizations, memberships)




