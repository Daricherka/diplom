from flask import Flask, request, json, Response, render_template
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
from settings import *
from framework import *
from database import *
from models import *
# Logging
import logging
from logging.handlers import WatchedFileHandler


app = Flask(__name__)
api = Api(app, catch_all_404s=True)
handler = WatchedFileHandler('api_error.log')
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
mysql = MySQL()
DB.mysql_config(app, mysql)
UserModel.secret_key = SECRET_KEY
UserModel.token_expire_time = TOKEN_EXPIRE_TIME


@app.before_request
def before_request():
    DB.mysql_connect(mysql)


@app.teardown_request
def teardown_request(exception):
    DB.connection.close()


@app.errorhandler(Exception)
def all_exception_handler(error):
    app.logger.error(error)


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Accept,Content-Length,Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS,HEAD')
  return response


def authenticate(function):
    def wrapper(*args, **kwargs):
        ### <for-testing> ###
        #return function(*args, **kwargs)
        token = request.headers.get('Authorization')
        if token != None:
            token = token.replace('"', '')
        if token == '01eb19b753d174c94a6383d5d42c697fc08e3502':
            return function(*args, **kwargs)
        ### </for-testing> ###

        token = request.headers.get('Authorization')

        if token == None:
            return Result.no_access()

        token = token.replace('"', '')

        result = UserModel.verify(DB.cursor, token)

        if not type(result) is dict:
            return Result.error()

        if result['type'] == True:
            if result['value'] == 2:
                DB.connection.commit()
            
            return function(*args, **kwargs)

        return Result.no_access(result)

    return wrapper


@app.route('/tdomain/')
def t_domain():
    return render_template('t_domain.html')


@app.route('/tscenario/')
def t_scenario():
    return render_template('t_scenario.html')


@app.route('/tds/')
def t_demand_source():
    return render_template('t_demand_sources.html')


# USER
@app.route("/tu/")
def test_user():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title></title>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
        <script type="text/javascript">
            var request = {
                "name": "qwerty",
                "email": "qwerty@test.com",
                "password": "qwerty",
                "active": 1,
            }
            console.log(request);
            $.ajax({
                url: '/management/api/users/',
                type: 'POST',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify(request),
                success: function(response) {
                    console.log(response);
                }
            });
        </script>
    </head>
    <body>

    </body>
    </html>
    '''


# USER
@app.route("/tl/")
def test_login():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title></title>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
        <script type="text/javascript">
            var request = {
                "nameOrEmail": "qwerty",
                "password": "qwerty",
            }
            console.log(request);
            $.ajax({
                url: '/management/api/login/',
                type: 'POST',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify(request),
                success: function(response) {
                    console.log(response);
                }
            });
        </script>
    </head>
    <body>

    </body>
    </html>
    '''


# USER
@app.route("/ta/")
def test_access():
    token = 'ed537d3377d398bf243f1b543c7861c8fdefaa87'
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title></title>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
        <script type="text/javascript">
            $.ajax({
                url: '/management/api/scenarios/',
                type: 'GET',
                dataType: 'json',
                beforeSend: function(xhr){xhr.setRequestHeader('Authorization', "''' + token + '''");},
                success: function(response) {
                    console.log(response);
                }
            });
        </script>
    </head>
    <body>

    </body>
    </html>
    '''


#########################################################################################################


######################
### Export Domains ###
######################
@authenticate
@app.route('/management/api/domain_lists/<int:id>/export/', methods=['POST', 'GET'])
def export_domains(id=None):
    result = ''

    if id != None:
        model_result = DomainModel.get_domain_name_list(DB.cursor, id)
        result = ','.join(model_result)

    #return Response(result, mimetype='application/octet-stream')

    headers = {
        'Content-Disposition': 'inline; filename="domains.csv"',
        'Content-Type': 'application/octet-stream;'
    }

    return result, 200, headers


#########################################################################################################


#####################
### Targeting Geo ###
#####################
class TargetingGeo(Resource):
    method_decorators = [authenticate]

    def get(self):
        search = GetFilter.search(1)

        if search == None:
            return Result.bad_request()

        result = GeoModel.get_search_list(DB.cursor, search)
        
        return Result.search(result, search)


########################
### Targeting Domain ###
########################
class TargetingDomain(Resource):
    method_decorators = [authenticate]

    def get(self):
        search = GetFilter.search(1)

        if search == None:
            return Result.bad_request()

        result = DomainModel.get_search_list(DB.cursor, search)
        
        return Result.search(result, search)


###########################
### Targeting Publisher ###
###########################
class TargetingPublisher(Resource):
    method_decorators = [authenticate]

    def get(self):
        search = GetFilter.search(1)

        if search == None:
            return Result.bad_request()

        result = PublisherModel.get_search_list(DB.cursor, search)
        
        return Result.search(result, search)


##########################
### Targeting Platform ###
##########################
class TargetingPlatform(Resource):
    method_decorators = [authenticate]

    def get(self):
        search = GetFilter.search(1)

        if search == None:
            return Result.bad_request()

        result = PlatformModel.get_search_list(DB.cursor, search)
        
        return Result.search(result, search)


#########################
### Targeting Browser ###
#########################
class TargetingBrowser(Resource):
    method_decorators = [authenticate]

    def get(self):
        search = GetFilter.search(1)

        if search == None:
            return Result.bad_request()

        result = BrowserModel.get_search_list(DB.cursor, search)
        
        return Result.search(result, search)


#####################
### Targeting OSS ###
#####################
class TargetingOSS(Resource):
    method_decorators = [authenticate]

    def get(self):
        search = GetFilter.search(1)

        if search == None:
            return Result.bad_request()

        result = OSSModel.get_search_list(DB.cursor, search)
        
        return Result.search(result, search)


########################
### Targeting Device ###
########################
class TargetingDevice(Resource):
    method_decorators = [authenticate]

    def get(self):
        search = GetFilter.search(1)

        if search == None:
            return Result.bad_request()

        result = DeviceModel.get_search_list(DB.cursor, search)

        return Result.search(result, search)


#########################################################################################################


##############
### Domain ###
##############
class Domain(Resource):
    method_decorators = [authenticate]

    # --- #
    # GET #
    # --- #
    def get(self, id=None):
        if id != None:
            return self.get_single(id)
        return self.get_list()

    # ----------- #
    # GET: Single #
    # ----------- #
    def get_single(self, id=None):
        result = DomainModel.get(DB.cursor, id)
        return Result.single(result, id)

    # --------- #
    # GET: List #
    # --------- # 
    def get_list(self):
        filters = Filter.default()
        result = DomainModel.get_list(DB.cursor, filters)
        return Result.list(result)

    # ---- #
    # POST #
    # ---- #
    def post(self, id=None):
        if id != None:
            return self.post_duplicate(id)
        return self.post_create()

    # ------------ #
    # POST: Create #
    # ------------ #
    def post_create(self):
        json_data = JsonFilter.domain_list()

        if json_data == None:
            return Result.bad_request()

        result = DomainModel.create(DB.cursor, json_data)

        if result != None:
            DB.connection.commit()

        return Result.create(result)

    # --------------- #
    # POST: Duplicate #
    # --------------- #
    def post_duplicate(self, id=None):
        result = DomainModel.duplicate(DB.cursor, id)

        if result != None:
            DB.connection.commit()

        return Result.duplicate(result, id)

    # --- #
    # PUT #
    # --- #
    def put(self, id=None):
        if id == None:
            return Result.bad_request()

        json_data = JsonFilter.domain_list()

        if json_data == None:
            return Result.bad_request()

        result = DomainModel.update(DB.cursor, id, json_data)

        if result != None:
            DB.connection.commit()

        return Result.update(result)

    # ----- #
    # PATCH #
    # ----- #
    def patch(self, id=None):
        archived = JsonFilter.archived()

        if id == None:
            return Result.bad_request()

        if archived != None:
            result = DomainModel.update_archive(DB.cursor, id, archived)
            DB.connection.commit()
            return Result.update(result)

        return Result.bad_request()

    # ------ #
    # DELETE #
    # ------ #
    def delete(self, id=None):
        if id == None:
            return Result.bad_request()

        result = DomainModel.delete(DB.cursor, id)

        if result == True:
            DB.connection.commit()

        return Result.delete(result)


#########################################################################################################


################
### Scenario ###
################
class Scenario(Resource):
    method_decorators = [authenticate]

    # --- #
    # GET #
    # --- #
    def get(self, id=None):
        if id != None:
            return self.get_single(id)
        return self.get_list()           
     
    # ----------- #
    # GET: Single #
    # ----------- #   
    def get_single(self, id=None):
        result = ScenarioModel.get_single(DB.cursor, id)
        return Result.single(result, id)

    # --------- #
    # GET: List #
    # --------- # 
    def get_list(self):
        filters = Filter.default()
        result = ScenarioModel.get_list(DB.cursor, filters)
        return Result.list(result)

    # ---- #
    # POST #
    # ---- #
    def post(self, id=None):
        if id != None:
            return self.post_duplicate(id)
        return self.post_create()

    # ------------ #
    # POST: Create #
    # ------------ #
    def post_create(self):
        json_data = JsonFilter.scenario()

        if json_data == None:
            return Result.bad_request()

        result = ScenarioModel.create(DB.cursor, json_data)

        if result != None:
            DB.connection.commit()

        return Result.create(result)

    # --------------- #
    # POST: Duplicate #
    # --------------- #
    def post_duplicate(self, id=None):
        result = ScenarioModel.duplicate(DB.cursor, id)

        if result != None:
            DB.connection.commit()

        return Result.duplicate(result, id)

    # --- #
    # PUT #
    # --- #
    def put(self, id=None):
        if id == None:
            return Result.bad_request()

        json_data = JsonFilter.scenario()

        if json_data == None:
            return Result.bad_request()

        result = ScenarioModel.update(DB.cursor, id, json_data)

        if result != None:
            DB.connection.commit()

        return Result.update(result)

    # ----- #
    # PATCH #
    # ----- #
    def patch(self, id=None):
        archived = JsonFilter.archived()

        if id == None:
            return Result.bad_request()

        if archived != None:
            result = ScenarioModel.update_archive(DB.cursor, id, archived);
            DB.connection.commit()
            return Result.update(result)

        return Result.bad_request()


############
### Tier ###
############
class Tier(Resource):
    method_decorators = [authenticate]

    # --- #
    # GET #
    # --- #
    def get(self, id=None):
        if id != None:
            return self.get_single(id)
        return self.get_list()

    # ----------- #
    # GET: Single #
    # ----------- #
    def get_single(self, id=None):
        result = TierModel.get_single(DB.cursor, id)
        return Result.single(result, id)

    # --------- #
    # GET: List #
    # --------- # 
    def get_list(self):
        filters = Filter.default()
        result = TierModel.get_list(DB.cursor, filters)
        return Result.list(result)

    # ----- #
    # PATCH #
    # ----- #
    def patch(self, id=None):
        archived = JsonFilter.archived()

        if id == None:
            return Result.bad_request()

        if archived != None:
            result = TierModel.update_archive(DB.cursor, id, archived);
            DB.connection.commit()
            return Result.update(result)

        return Result.bad_request()


#####################
### Demand Source ###
#####################
class DemandSource(Resource):
    method_decorators = [authenticate]

    # --- #
    # GET #
    # --- #
    def get(self, id=None):
        if id != None:
            return self.get_single(id)
        return self.get_list()

    # ----------- #
    # GET: Single #
    # ----------- #
    def get_single(self, id):
        result = DemandSourceModel.get_single(DB.cursor, id)
        return Result.single(result, id)

    # --------- #
    # GET: List #
    # --------- #
    def get_list(self):
        filters = Filter.default()
        result = DemandSourceModel.get_list(DB.cursor, filters)
        return Result.list(result)

    # ---- #
    # POST #
    # ---- #
    def post(self, id=None):
        if id != None:
            return self.post_duplicate(id)
        return self.post_create()

    # ------------ #
    # POST: Create #
    # ------------ #
    def post_create(self):
        json_data = JsonFilter.demand_source()

        if json_data == None:
            return Result.bad_request()

        result = DemandSourceModel.create(DB.cursor, json_data)

        if result != None:
            DB.connection.commit()

        return Result.create(result)

    # --------------- #
    # POST: Duplicate #
    # --------------- #
    def post_duplicate(self, id=None):
        result = DemandSourceModel.duplicate(DB.cursor, id)

        if result != None:
            DB.connection.commit()

        return Result.duplicate(result, id)

    # --- #
    # PUT #
    # --- #
    def put(self, id=None):
        if id == None:
            return Result.bad_request()

        json_data = JsonFilter.demand_source()

        if json_data == None:
            return Result.bad_request()

        result = DemandSourceModel.update(DB.cursor, id, json_data)

        if result != None:
            DB.connection.commit()

        return Result.update(result)

    # ----- #
    # PATCH #
    # ----- #
    def patch(self, id=None):
        archived = JsonFilter.archived()
        enabled = JsonFilter.enabled()

        if id == None:
            return Result.bad_request()

        if archived != None:
            result = DemandSourceModel.update_archive(DB.cursor, id, archived)
            DB.connection.commit()
            return Result.update(result)
        elif enabled != None:
            result = DemandSourceModel.update_enable(DB.cursor, id, enabled)
            DB.connection.commit()
            return Result.update(result)

        return Result.bad_request()


############
### User ###
############
class User(Resource):
    method_decorators = [authenticate]

    # --- #
    # GET #
    # --- #
    def get(self, id=None):
        if id != None:
            return self.get_single(id)
        return self.get_list()

    # ----------- #
    # GET: Single #
    # ----------- #
    def get_single(self, id):
        result = UserModel.get_single(DB.cursor, id)
        return Result.single(result, id)

    # --------- #
    # GET: List #
    # --------- #
    def get_list(self):
        result = UserModel.get_list(DB.cursor)
        return Result.list(result)

    # ---- #
    # POST #
    # ---- #
    def post(self, id=None):
        if id != None:
            return self.post_duplicate(id)
        return self.post_create()

    # ------------ #
    # POST: Create #
    # ------------ #
    def post_create(self):
        json_data = JsonFilter.user()

        if json_data == None:
            return Result.bad_request()

        result = UserModel.create(DB.cursor, json_data)

        if not type(result) is dict:
            return Result.error()

        if not 'type' in result:
            return Result.error()

        if result['type'] == 'success':
            DB.connection.commit()

        return Result.create_user(result)

    # --------------- #
    # POST: Duplicate #
    # --------------- #
    def post_duplicate(self, id=None):
        return Result.bad_request()

    # --- #
    # PUT #
    # --- #
    def put(self, id=None):
        if id == None:
            return Result.bad_request()

        json_data = JsonFilter.user(update=True)

        if json_data == None:
            return Result.bad_request()

        result = UserModel.update(DB.cursor, id, json_data)

        if not type(result) is dict:
            return Result.error()

        if not 'type' in result:
            return Result.error()

        if result['type'] == 'success':
            DB.connection.commit()

        return Result.update_user(result)

    # ----- #
    # PATCH #
    # ----- #
    def patch(self, id=None):
        active = JsonFilter.active()

        if id == None:
            return Result.bad_request()

        if active != None:
            result = UserModel.update_active(DB.cursor, id, active);
            DB.connection.commit()
            return Result.update(result)

        return Result.bad_request()


#############
### Login ###
#############
class Login(Resource):
    # ---- #
    # POST #
    # ---- #
    def post(self):
        json_data = JsonFilter.login()

        if json_data == None:
            return Result.bad_request()
        
        result = UserModel.login(DB.cursor, json_data['nameOrEmail'], json_data['password'])

        if result != None:
            DB.connection.commit()

        return Result.login(result)


#########################################################################################################


# Targeting
api.add_resource(TargetingGeo, '/management/api/targeting_information/geos/')
api.add_resource(TargetingDomain,  '/management/api/targeting_information/domains/')
api.add_resource(TargetingPublisher, '/management/api/targeting_information/publishers/')
api.add_resource(TargetingPlatform, '/management/api/targeting_information/platforms/')
api.add_resource(TargetingBrowser, '/management/api/targeting_information/browsers/')
api.add_resource(TargetingOSS, '/management/api/targeting_information/oss/')
api.add_resource(TargetingDevice, '/management/api/targeting_information/devices/')

# Domain
api.add_resource(Domain, '/management/api/domain_lists/',
                         '/management/api/domain_lists/<int:id>/')

# Scenario
api.add_resource(Scenario, '/management/api/scenarios/', 
                           '/management/api/scenarios/<int:id>/')

# Tier (for testing only)
api.add_resource(Tier, '/management/api/tiers/', 
                       '/management/api/tiers/<int:id>/')

# Demand Source
api.add_resource(DemandSource, '/management/api/demand_sources/', 
                               '/management/api/demand_sources/<int:id>/')

# Users
api.add_resource(User, '/management/api/users/', 
                       '/management/api/users/<int:id>/')

# Login
api.add_resource(Login, '/management/api/login/')


#########################################################################################################


if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)