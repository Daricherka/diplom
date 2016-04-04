from flask import request
import jsonschema
import re


######################
### Get Validation ###
######################
class GetFilter(object):
    # ------ #
    # Search #
    # ------ #
    @staticmethod
    def search(min=0):
        data = request.args.get('search')
        
        if data == None:
            return None

        if len(data) < min:
            return None

        if type(data) is int:
            data = str(data)

        pattern = re.compile(r'^[a-zA-Z0-9\s.,-]*$')
        
        if not pattern.match(data):
            return None
        
        return str(data)

    # -------- #
    # Archived #
    # -------- #
    @staticmethod
    def archived(min=0):
        data = request.args.get('archived')

        if data == None:
            return None

        if type(data) is int:
            data = str(data)

        if data == '1':
            return 1

        return 0


#######################
### Json Validation ###
#######################
class JsonFilter(object):
    # ----------- #
    # Domain List #
    # ----------- #
    @staticmethod
    def domain_list():
        json_schema = {
            'type': 'object',
            'properties': {
                'id': {'type': 'number'},
                'name': {'type': 'string'},
                'description': {'type': 'string'},
                'archived': {'type': 'number'},
                'domains': {
                    'type': 'array',
                    'minItems': 0,
                    'items': {
                        'type': 'string',
                    },
                },
            },
            'required': [
                'name',
                'description',
                'archived',
                'domains'
            ],
        }

        json_data = request.get_json(force=True)

        if json_data == None:
            return None

        try:
            jsonschema.validate(json_data, json_schema)
        except jsonschema.ValidationError:
            print 'Json Data Error'
            return None
        except jsonschema.SchemaError:
            print 'Json Schema Error'
            return None

        return json_data

    # -------- #
    # Archived #
    # -------- #
    @staticmethod
    def archived():
        json_data = request.get_json(force=True)

        if 'archived' in json_data:
            data = json_data['archived']

            if type(data) is int:
                data = str(data)

            if data == '1':
                return 1

            return 0

        return None

    # ------- #
    # Enabled #
    # ------- #
    @staticmethod
    def enabled():
        json_data = request.get_json(force=True)

        if 'enabled' in json_data:
            data = json_data['enabled']

            if type(data) is int:
                data = str(data)

            if data == '1':
                return 1
                
            return 0

        return None

    # ------ #
    # Active #
    # ------ #
    @staticmethod
    def active():
        json_data = request.get_json(force=True)

        if 'active' in json_data:
            data = json_data['active']

            if type(data) is int:
                data = str(data)

            if data == '1':
                return 1
                
            return 0

        return None

    # -------- #
    # Scenario #
    # -------- #
    @staticmethod
    def scenario():
        json_schema = {
            'type': 'object',
            'properties': {
                'id': {'type': 'number'},
                'name': {'type': 'string'},
                'description': {'type': 'string'},
                'archived': {'type': 'number'},
                'tiers': {
                    'type': 'array',
                    'minItems': 0,
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'number'},
                            'name': {'type': ['string', 'null']},
                            'order': {'type': 'number'},
                            'timeout': {'type': 'number'},
                            'demandSources': {
                                'type': 'array',
                                'minItems': 0,
                                'items': {
                                    'type': 'number',
                                },
                            },
                        },
                        'required': [
                            'name',
                            'order',
                            'timeout',
                            'demandSources',
                        ],
                    },
                },
            },
            'required': [
                'name',
                'description',
                'archived',
                'tiers',
            ],
        }    

        json_data = request.get_json(force=True)

        if json_data == None:
            return None

        try:
            jsonschema.validate(json_data, json_schema)
        except jsonschema.ValidationError:
            print 'Json Data Error'
            return None
        except jsonschema.SchemaError:
            print 'Json Schema Error'
            return None

        return json_data

    # ------------- #
    # Demand Source #
    # ------------- #
    @staticmethod
    def demand_source():
        json_schema = {
            'type': 'object',
            'properties': {
                'id': {'type': 'number'},
                'name': {'type': 'string'},
                'description': {'type': 'string'},
                'type': {'type': ['string', 'null']},
                'url': {'type': 'string'},
                'floorCPM': {'type': 'number'},
                'reqTimeout': {'type': 'number'},
                'frequencyCap': {'type': 'number'},
                'frequencyCapMode': {'type': 'number'},
                'requestsCap': {'type': 'number'}, 
                'requestsCapMode': {'type': 'number'}, 
                'viewsCap': {'type': 'number'},
                'viewsCapMode': {'type': 'number'},
                'inFlightEnd': {'type': ['string', 'null']},
                'inFlightStart': {'type': 'string'},
                'inFlightTimeZone': {'type': 'number'},
                'enabled': {'type': 'number'},
                'archived': {'type': 'number'},
                'targeting': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'number'},
                        'name': {'type': 'string'},
                        'filters': {
                            'type': 'array',
                            'minItems': 0,
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'list': {
                                        'type': 'array',
                                        'minItems': 0,
                                        'items': {
                                            'type': ['number', 'string'],
                                        },
                                    },
                                    'mode': {'type': 'number'},
                                    'type': {'type': 'string'},
                                },
                                'required': [
                                    'list',
                                    'mode',
                                ],
                            },
                        }, 
                        'inFlightTimeMatrix': {
                            'type': 'object',
                            'properties': {
                                'zone': {'type': 'number'}, 
                                'list': {
                                    'type': 'array',
                                    'minItems': 0,
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'dayId': {'type': 'number'},
                                            'startTimeId': {'type': 'number'},
                                            'endTimeId': {'type': 'number'},
                                        },
                                        'required': [
                                            'dayId',
                                            'startTimeId',
                                            'endTimeId',
                                        ],
                                    },
                                }, 
                                'mode': {'type': 'number'},
                            }
                        }
                    },
                    'required': [
                        'name',
                        'filters',
                        'inFlightTimeMatrix',
                    ],
                },
            },
            'required': [
                'name',
                'description',
                'type',
                'url',
                'floorCPM',
                'reqTimeout',
                'frequencyCap',
                'frequencyCapMode',
                'requestsCap',
                'requestsCapMode',
                'viewsCap',
                'viewsCapMode',
                'inFlightEnd',
                'inFlightStart',
                'inFlightTimeZone',
                'enabled',
                'archived',
                'targeting',
            ],
        }

        json_data = request.get_json(force=True)

        if json_data == None:
            return None

        try:
            jsonschema.validate(json_data, json_schema)
        except jsonschema.ValidationError as e:
            print 'Json Data Error'
            print e
            return None
        except jsonschema.SchemaError as e:
            print 'Json Schema Error'
            print e
            return None

        return json_data

    # ---- #
    # User #
    # ---- #
    @staticmethod
    def user(update=False):
        json_schema = {
            'type': 'object',
            'properties': {
                'id': {'type': 'number'},
                'name': {
                    'type': 'string',
                    'minLength': 5, 
                    'maxLength': 32,
                },
                'email': {'type': 'string'},
                'password': {
                    'type': 'string',
                    'minLength': 5,
                },
                'active': {'type': 'number'},
            },
            'required': [
                'name',
                'email',
                'password',
                'active',
            ],
        }

        if update == True:
            json_schema['properties']['password']['type'] = ['string', 'null']

        json_data = request.get_json(force=True)

        if json_data == None:
            return None

        try:
            jsonschema.validate(json_data, json_schema)
        except jsonschema.ValidationError:
            print 'Json Data Error'
            return None
        except jsonschema.SchemaError:
            print 'Json Schema Error'
            return None

        return json_data

    # ----- #
    # Login #
    # ----- #
    @staticmethod
    def login():
        json_schema = {
            'type': 'object',
            'properties': {
                'nameOrEmail': {'type': 'string'},
                'password': {'type': 'string'},
            },
            'required': [
                'nameOrEmail',
                'password',
            ],
        }

        json_data = request.get_json(force=True)

        if json_data == None:
            return None

        try:
            jsonschema.validate(json_data, json_schema)
        except jsonschema.ValidationError:
            print 'Json Data Error'
            return None
        except jsonschema.SchemaError:
            print 'Json Schema Error'
            return None

        return json_data


##############
### Filter ###
##############
class Filter(object):
    # --------- #
    # Get By Id #
    # --------- #
    @staticmethod
    def default():
        filters = {
            'archived': GetFilter.archived(),
            'search': GetFilter.search()
        }

        return filters


#######################
### Response Format ###
#######################
class Result(object):
    # ----- #
    # Login #
    # ----- #
    @staticmethod
    def login(data):
        if data == None:
            result = {
                'message': 'Active User Not Found'
            }

            return result, 403

        result = {
            'data': data,
            'message': 'Success'
        }

        return result, 200

    # ---- #
    # List #
    # ---- #
    @staticmethod
    def list(data):
        if data == None:
            return Result.empty_list()

        if type(data) in [list, tuple]:
            if len(data) == 0:
                return Result.empty_list()
        
            result = {
                'list': data,
                'message': 'Success'
            }

            return result, 200

        return Result.error()

    # ------ #
    # Single #
    # ------ #
    @staticmethod
    def single(data, request_id):
        if data == None:
            return Result.empty_single(request_id)

        if type(data) is dict:
            if len(data.keys()) == 0:
                return Result.empty_single(request_id)

            result = {
                'data': data,
                'requestId': int(request_id),
                'message': 'Success'
            }

            return result, 200

        return Result.error()

    # ------ #
    # Search #
    # ------ #
    @staticmethod
    def search(data, search):
        if data == None:
            return Result.empty_search(search)

        if type(data) in [list, tuple]:
            if len(data) == 0:
                return Result.empty_search(search)
        
            result = {
                'list': data,
                'requestSearch': search,
                'message': 'Success'
            }

            return result, 200

        return Result.error()

    # ------ #
    # Create #
    # ------ #
    @staticmethod
    def create(id):
        if id != None:
            result = {
                'id': int(id),
                'message': 'Created'
            }

            return result, 201  

        return Result.error()

    # ----------- #
    # Create User #
    # ----------- #
    @staticmethod
    def create_user(data):
        if not type(data) is dict:
            return Result.error()

        if not 'type' in data:
            return Result.error()

        if not 'value' in data:
            return Result.error()

        if data['type'] == 'error':
            if data['value'] == 1:
                result = {
                    'message': 'Username already exists'
                }

                return result, 409
                
            elif data['value'] == 2:
                result = {
                    'message': 'Email already exists'
                }

                return result, 409

        elif data['type'] == 'success':
            return Result.create(int(data['value']))

        return Result.error()

    # --------- #
    # Duplicate #
    # --------- #
    @staticmethod
    def duplicate(id, request_id):
        if id != None:
            result = {
                'id': int(id),
                'requestId': int(request_id),
                'message': 'Duplicated'
            }

            return result, 201

        return Result.error()

    # ------ #
    # Update #
    # ------ #
    @staticmethod
    def update(id):
        if id != None:
            result = {
                'id': int(id),
                'message': 'Updated'
            }

            return result, 200  

        return Result.error()

    # ----------- #
    # Update User #
    # ----------- #
    @staticmethod
    def update_user(data):
        if not type(data) is dict:
            return Result.error()

        if not 'type' in data:
            return Result.error()

        if not 'value' in data:
            return Result.error()

        if data['type'] == 'error':
            if data['value'] == 1:
                result = {
                    'message': 'Username already exists'
                }

                return result, 400
                
            elif data['value'] == 2:
                result = {
                    'message': 'Email already exists'
                }

                return result, 400

        elif data['type'] == 'success':
            return Result.update(int(data['value']))

        return Result.error()

    # ------ #
    # Delete #
    # ------ #
    @staticmethod
    def delete(deleted):
        if deleted == True:
            result = {
                'message': 'Deleted'
            }

            return result, 200  

        return Result.error()

    # ---------- #
    # Empty List #
    # ---------- #
    @staticmethod
    def empty_list():
        result = {
            'list': [],
            'message': 'Empty List'
        }

        return result, 200

    # ------------ #
    # Empty Search #
    # ------------ #
    @staticmethod
    def empty_search(search):
        result = {
            'list': [],
            'search': search,
            'message': 'Empty List'
        }

        return result, 200

    # ------------ #
    # Empty Single #
    # ------------ #
    @staticmethod
    def empty_single(request_id):
        result = {
            'data': None,
            'requestId': int(request_id),
            'message': 'Data Not Found'
        }

        return result, 404

    # ------------- #
    # Strange Error #
    # ------------- #
    @staticmethod
    def error():
        result = {
            'message': 'Unknown Error'
        }

        return result, 500

    # ----------- #
    # Bad Request #
    # ----------- #
    @staticmethod
    def bad_request():
        result = {
            'message': 'Bad Request'
        }

        return result, 400

    # --------- #
    # No Access #
    # --------- #
    @staticmethod
    def no_access(data=None):
        if data == None:
            result = {
                'message': 'Access is denied'
            }

            return result, 403

        if not type(data) is dict:
            return Result.error()

        if data['type'] != False:
            return Result.error()

        if data['value'] == 1:
            result = {
                'message': 'Access is denied'
            }

            return result, 403

        if data['value'] == 2:
            result = {
                'message': 'Token expired'
            }

            return result, 401

        return Result.error()


##################
### Pagination ###
##################
class Pagination(object):
    default_per_page = 5

    def __init__(self, page, per_page):
        if page == None:
            page = 1

        if per_page == None:
            per_page = self.default_per_page

        self.page = int(page)
        self.per_page = int(per_page)
        self.start = (self.page - 1) * self.per_page
        self.count = self.per_page