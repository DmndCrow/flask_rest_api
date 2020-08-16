from flask import Blueprint, request, jsonify
from .neo4j_connection import Neo4jConn
from .elasticsearch_connection import ElasticsearchConn
from . import settings

api = Blueprint('api', __name__)

neorj_conn = Neo4jConn(
        url=f'neo4j://{settings.NEO4J_HOST}:{settings.NEO4J_PORT}',
        login=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )


es_conn = ElasticsearchConn(settings.ES_INDEX)


def _return_405_error():
    return jsonify({'message': 'Oops'}), 405


# @api.route('/api/person', methods=['POST'])
# def api_create_person():
#     if request.method == 'POST':
#         return jsonify({'message': 'create person'}), 201
#     else:
#         return _return_405_error()


@api.route('/api/person/all', methods=['GET', 'DELETE'])
def api_handle_person_all():
    if request.method == 'GET':
        return jsonify({'message':  'get all people'}), 200
    elif request.method == 'DELETE':
        return jsonify({'message': 'delete all people'}), 200
    else:
        return _return_405_error()


# @api.route('/api/person/<_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
# def api_handle_person_by_id(_id: str):
#     if request.method == 'GET':
#         return jsonify({'message': 'get person with id=' + _id}), 200
#     elif request.method in ['PATCH', 'PUT']:
#         return jsonify({'message': 'update person with id=' + _id}), 200
#     elif request.method == 'DELETE':
#         return jsonify({'message': 'delete person with id=' + _id}), 200
#     else:
#         return _return_405_error()
#
#
# @api.route('/api/person/<_id>/organization', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
# def api_handle_organization_by_person_id(_id: str):
#     if request.method == 'GET':
#         return jsonify({'message': 'get organization with person_id=' + _id}), 200
#     elif request.method in ['PATCH', 'PUT']:
#         return jsonify({'message': 'update organization with person_id=' + _id}), 200
#     elif request.method == 'DELETE':
#         return jsonify({'message': 'delete connection to organization with person_id=' + _id}), 200
#     else:
#         return _return_405_error()
#
#
# @api.route('/api/organization', methods=['POST'])
# def create_organization():
#     if request.method == 'POST':
#         return jsonify({'message': 'create organization'}), 201
#     else:
#         return _return_405_error()
#
#
# @api.route('/api/organization/all', methods=['GET', 'DELETE'])
# def api_handle_organization_all():
#     if request.method == 'GET':
#         return jsonify({'message': 'get all organizations'}), 200
#     elif request.method == 'DELETE':
#         return jsonify({'message': 'delete all organizations'}), 200
#     else:
#         return _return_405_error()
#
#
# @api.route('/api/organization/<_group_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
# def api_handle_organization_by_group_id(_group_id: str):
#     if request.method == 'GET':
#         return jsonify({'message': 'get organization with _group_id=' + _group_id}), 200
#     elif request.method in ['PATCH', 'PUT']:
#         return jsonify({'message': 'update organization with _group_id=' + _group_id}), 200
#     elif request.method == 'DELETE':
#         return jsonify({'message': 'delete organization with _group_id=' + _group_id}), 200
#     else:
#         return _return_405_error()
#
#
# @api.route('/api/organization/<_group_id>/person', methods=['GET'])
# def api_handle_person_by_group_id(_group_id: str):
#     if request.method == 'GET':
#         return jsonify({'message': 'get all person with group_id=' + _group_id}), 200
#     else:
#         return _return_405_error()
