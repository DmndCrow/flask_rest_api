# Documentation

* GET ```/api/build``` - load data from csv and upload to neo4j and elasticsearch if they are empty

### Person
* POST ```/api/person``` - create person using data from request body
* GET ```/api/person/all``` - get all person from db
* GET ```/api/person/<id>``` - get person by id
* PUT/PATCH ```/api/person/<id>``` - update person by id using data from request body
* DELETE ```/api/person/<id>``` - delete person by id from db

##### Fields of Person that will be used in request:
1. id: string, unique
2. name: string
3. email: string
4. alias: string
5. nationality: string

### Organization
* POST ```/api/organization``` - create organization using data from request body
* GET ```/api/organization/all``` - get all organization from db
* GET ```/api/organization/<group_id>``` - get organization by group_id
* PUT/PATCH ```/api/organization/<group_id>``` - update organization by group_id using data from request body
* DELETE ```/api/organization/<group_id>``` - delete organization by group_id from db

##### Fields of Organization that will be used in request:
1. group_id: string, unique
2. name: string

### Memberships
* GET ```/api/membership/person/<id>``` - get organization that a person MEMBER_OF using id
* POST ```/api/membership/person/<id>``` - create new relationship by providing group_id in request body
* PUT/PATCH ```/api/membership/person/<id>``` - connect person to new organization by providing group_id in request body
* DELETE ```/api/membership/person/<id>``` - delete relation of the person with given id
* GET ```/api/membership/organization/<group_id>``` - get all person that are MEMBER_OF organization using group_id