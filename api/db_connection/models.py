import json
import uuid


class Organization:
    def __init__(self, csv_list=None, db_dict=None, user_dict=None):
        if csv_list:
            self.group_id = csv_list[7]
            self.name = csv_list[6]
        elif db_dict:
            self.group_id = db_dict['group_id']
            self.name = db_dict['name']
        elif user_dict:
            self.group_id = str(uuid.uuid4())
            self.name = user_dict['name'] if 'name' in user_dict else ''

    def __repr__(self):
        return f'{self.name} with id={self.group_id}'


class Person:
    def __init__(self, csv_list=None, db_dict=None, user_dict=None):
        if csv_list:
            self.id = csv_list[0]
            self.name = csv_list[1]
            self.alias = csv_list[2]
            self.email = csv_list[3]
            self.nationality = 'GB'
        elif db_dict:
            self.id = db_dict['id']
            self.name = db_dict['name']
            self.alias = db_dict['alias']
            self.email = db_dict['email']
            self.nationality = db_dict['nationality']
        elif user_dict:
            self.id = str(uuid.uuid4())
            self.name = user_dict['name'] if 'name' in user_dict else ''
            self.alias = user_dict['alias'] if 'alias' in user_dict else ''
            self.email = user_dict['email'] if 'email' in user_dict else ''
            self.nationality = user_dict['nationality'] if 'nationality' in user_dict else 'GB'

    def __repr__(self):
        return f'{self.alias} with id={self.id}'
