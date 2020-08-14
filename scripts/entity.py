class Organization:
    def __init__(self, _line):
        self.group_id = _line[7]
        self.name = _line[6]

    def __repr__(self):
        return f'{self.name} with id={self.group_id}'


class Person:
    def __init__(self, _line):
        self.id = _line[0]
        self.name = _line[1]
        self.alias = _line[2]
        self.email = _line[3]
        self.nationality = 'GB'

    def __repr__(self):
        return f'{self.alias} with id={self.id}'
