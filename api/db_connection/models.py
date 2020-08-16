import json


class Organization:
    def __init__(self, csv_list=None, db_dict=None):
        if csv_list:
            self.group_id = csv_list[7]
            self.name = csv_list[6]
        else:
            self.group_id = db_dict['group_id']
            self.name = db_dict['name']

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
            self.id = user_dict['id'] if 'id' in user_dict else hash(json.dumps(user_dict))
            self.name = user_dict['name'] if 'name' in user_dict else None
            self.alias = user_dict['alias'] if 'alias' in user_dict else None
            self.email = user_dict['email'] if 'email' in user_dict else None
            self.nationality = user_dict['nationality'] if 'nationality' in user_dict else None

    def __repr__(self):
        return f'{self.alias} with id={self.id}'
