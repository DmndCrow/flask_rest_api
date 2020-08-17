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


@api.route('/api/membership/person/<_id>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def api_handle_membership_by_person_id(_id: str):
    if request.method == 'GET':
        # find person by id
        res, code = es_conn.get_person_by_id(_id)
        # check whether person with given id exists
        if code == 200:
            # get organization
            res = neorj_conn.get_person_organization(_id)
        return jsonify({'message': res}), code
    elif request.method == 'POST':
        # to be sure we have new group_id to connect
        if 'group_id' in request.json:
            # find person with given id
            _, person_code = es_conn.get_person_by_id(_id)
            # and find org with given group_id from request body
            _, org_code = es_conn.get_organization_by_group_id(request.json['group_id'])
            if person_code and org_code:
                # try to make relation
                res, code = neorj_conn.create_membership(_id, request.json['group_id'])
                return jsonify({'message': res}), code
            else:
                return jsonify({'message': 'No person or organization'}), 404
        else:
            return jsonify({'message': {'Group id is not provided'}}), 404
    elif request.method in ['PUT', 'PATCH']:
        # check if request body has new group id
        if 'group_id' in request.json:
            # find person by id
            _, person_code = es_conn.get_person_by_id(_id)
            print(person_code, 'person')
            # and find org by new group id
            _, org_code = es_conn.get_organization_by_group_id(request.json['group_id'])
            print(org_code, 'org')
            if person_code == 200 and org_code == 200:
                # get current org of a person
                org = neorj_conn.get_person_organization(_id)
                print(org, 'org1')
                # if there is one org that person belongs to, remove relation
                if len(org):
                    print('delete')
                    neorj_conn.delete_membership(_id)
                # create new membership
                print('create')
                res, code = neorj_conn.create_membership(_id, request.json['group_id'])
                return jsonify({'message': res}), code
            return jsonify({'message': []}), 404
        else:
            return jsonify({'message': {'Group id is not provided'}}), 404
    elif request.method == 'DELETE':
        res, code = es_conn.get_person_by_id(_id)
        org = neorj_conn.get_person_organization(_id)
        if code == 200 and len(org):
            res, code = neorj_conn.delete_membership(_id)
            return jsonify({'message', res}), code
        return jsonify({'message': 'No such user or relation with org'}), 404
    else:
        return _return_405_error()


@api.route('/api/membership/organization/<_group_id>', methods=['GET'])
def api_handle_membership_by_group_id(_group_id: str):
    if request.method == 'GET':
        res = neorj_conn.get_organization_person(_group_id)
        return jsonify({'message': res}), 200
    else:
        return _return_405_error()
