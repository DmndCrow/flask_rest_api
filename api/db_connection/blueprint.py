from flask import Blueprint, request, jsonify
from .neo4j_connection import Neo4jConn
from .elasticsearch_connection import ElasticsearchConn
from . import settings
from .models import Person, Organization

api = Blueprint('api', __name__)

neorj_conn = Neo4jConn(
    url=f'neo4j://{settings.NEO4J_HOST}:{settings.NEO4J_PORT}',
    login=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD
)
es_conn = ElasticsearchConn(host=settings.ES_HOST, port=settings.ES_PORT)


def _return_405_error():
    return jsonify({'message': 'Oops'}), 405


# DONE
@api.route('/api/person', methods=['POST'])
def api_create_person():
    if request.method == 'POST':
        # generate person from request body
        person = Person(user_dict=request.json)
        # since newly generated id may exist, we get person with unique id to pass to neo4j
        person = es_conn.create_person(person)
        neorj_conn.create_person(person)
        return jsonify({'message': person.__dict__}), 201
    else:
        return _return_405_error()


# DONE
@api.route('/api/person/all', methods=['GET'])
def api_handle_person_all():
    if request.method == 'GET':
        res, _ = es_conn.get_person_by_id()
        return jsonify({'message':  res}), 200
    else:
        return _return_405_error()


# DONE
@api.route('/api/person/<_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def api_handle_person_by_id(_id: str):
    if request.method == 'GET':
        res, code = es_conn.get_person_by_id(_id)
        return jsonify({'message': res}), code
    elif request.method in ['PATCH', 'PUT']:
        # get Person from request body
        person = Person(user_dict=request.json)
        # but instead of newly generated id, use id passed as a parameter
        person.id = _id
        # update person
        # if exists return 200, else 404
        res = es_conn.update_person(person)
        # update in neo4j only if person exists
        if res == 200:
            neorj_conn.update_person(person)
        return jsonify({'message': person.__dict__}), res
    elif request.method == 'DELETE':
        # delete by id
        # return 200 if person with given id exists else 404
        code = es_conn.delete_person(_id)
        # delete only if person exists
        if code == 200:
            neorj_conn.delete_person(_id)
        return jsonify({}), code
    else:
        return _return_405_error()


# DONE
@api.route('/api/organization', methods=['POST'])
def create_organization():
    # same as create_person()
    if request.method == 'POST':
        organization = Organization(user_dict=request.json)
        organization = es_conn.create_organization(organization)
        neorj_conn.create_organization(organization)
        return jsonify({'message': organization.__dict__}), 201
    else:
        return _return_405_error()


# DONE
@api.route('/api/organization/all', methods=['GET'])
def api_handle_organization_all():
    if request.method == 'GET':
        res, _ = es_conn.get_organization_by_group_id()
        return jsonify({'message': res}), 200
    else:
        return _return_405_error()


# DONE
@api.route('/api/organization/<_group_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def api_handle_organization_by_group_id(_group_id: str):
    # same as in api_handle_person_by_id()
    if request.method == 'GET':
        res, code = es_conn.get_organization_by_group_id(_group_id)
        return jsonify({'message': res}), code
    elif request.method in ['PATCH', 'PUT']:
        organization = Organization(user_dict=request.json)
        organization.group_id = _group_id
        res = es_conn.update_organization(organization)
        if res == 200:
            neorj_conn.update_organization(organization)
        return jsonify({'message': organization.__dict__}), res
    elif request.method == 'DELETE':
        code = es_conn.delete_organization(_group_id)
        if code == 200:
            neorj_conn.delete_organization(_group_id)
        return jsonify({}), code
    else:
        return _return_405_error()


@api.route('/api/membership/person/<_id>', methods=['GET'])
def api_handle_membership_by_person_id(_id: str):
    if request.method == 'GET':
        return jsonify({'message': 'get organization with person_id=' + _id}), 200
    else:
        return _return_405_error()


@api.route('/api/membership/organization/<_group_id>', methods=['GET'])
def api_handle_membership_by_group_id(_group_id: str):
    if request.method == 'GET':
        return jsonify({'message': 'get organization with person_id=' + _group_id}), 200
    else:
        return _return_405_error()