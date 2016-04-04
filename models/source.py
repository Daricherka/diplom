from functions import *
from datetime import datetime
from targeting import *
from matrix import *


def to_iso_8601(date):
    if date != None:
        #return date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        return date.strftime('%Y-%m-%dT%H:%M:%S')
    return None


def from_iso_8601(date):
    if date != None:
        return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
    return None


#####################
### Demand Source ###
#####################
class DemandSourceModel(object):
    # ---------- #
    # Count Rows #
    # ---------- #
    @staticmethod
    def get_count(cursor):
        sql = "SELECT \
               count(`id`) AS `count` \
               FROM `demand_source`"

        cursor.execute(sql)
        result = cursor.fetchone()

        if result != None:
            return result['count']
        return 0

    # --------- #
    # Get By Id #
    # --------- #
    @staticmethod
    def get_single(cursor, id):
        sql = "SELECT \
               `d`.`id` AS `d.id`, \
               `d`.`name` AS `d.name`, \
               `d`.`description` AS `d.description`, \
               `d`.`type` AS `d.type`, \
               `d`.`url` AS `d.url`, \
               `d`.`floorCPM` AS `d.floor_cpm`, \
               `d`.`reqTimeout` AS `d.timeout`, \
               `d`.`requestsCap` AS `d.requests_cap`, \
               `d`.`requestsCapMode` AS `d.requests_cap_mode`, \
               `d`.`viewsCap` AS `d.views_cap`, \
               `d`.`viewsCapMode` AS `d.views_cap_mode`, \
               `d`.`frequencyCap` AS `d.frequency_cap`, \
               `d`.`frequencyCapMode` AS `d.frequency_cap_mode`, \
               `d`.`enabled` AS `d.enabled`, \
               `d`.`inFlightStart` AS `d.in_flight_start`, \
               `d`.`inFlightEnd` AS `d.in_flight_end`, \
               `d`.`inFlightTimeZone` AS `d.in_flight_time_zone`, \
               `d`.`targeting_id` AS `d.targeting_id` , \
               `d`.`archived` AS `d.archived` , \
               `t`.`id` AS `t.id`, \
               `t`.`name` AS `t.name`, \
               `t`.`geosMode` AS `t.geos_mode`, \
               `t`.`domainsMode` AS `t.domains_mode`, \
               `t`.`domainStringsMode` AS `t.domain_strings_mode`, \
               `t`.`publishersMode` AS `t.publishers_mode`, \
               `t`.`platformsMode` AS `t.platforms_mode`, \
               `t`.`browsersMode` AS `t.browsers_mode`, \
               `t`.`ossMode` AS `t.oss_mode`, \
               `t`.`devicesMode` AS `t.devices_mode`, \
               `t`.`inFlightTimeMatrixTimeZone` AS `t.in_flight_time_matrix_time_zone`, \
               `t`.`inFlightTimeMatrixMode` AS `t.in_flight_time_matrix_mode` \
               FROM `demand_source` AS `d` \
               LEFT JOIN targeting AS `t` \
               ON `d`.`targeting_id` = `t`.`id`\
               WHERE `d`.`id` = $id"

        replace = dict(id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchone()
        result = {}

        if db_result != None:
            targeting_id = db_result['d.targeting_id']

            result = {
                'id':               db_result['d.id'],
                'name':             db_result['d.name'],
                'description':      db_result['d.description'],
                'type':             db_result['d.type'],
                'url':              db_result['d.url'],
                'floorCPM':         db_result['d.floor_cpm'],
                'reqTimeout':       db_result['d.timeout'],
                'requestsCap':      db_result['d.requests_cap'],
                'requestsCapMode':  db_result['d.requests_cap_mode'],
                'viewsCap':         db_result['d.views_cap'],
                'viewsCapMode':     db_result['d.views_cap_mode'],
                'frequencyCap':     db_result['d.frequency_cap'],
                'frequencyCapMode': db_result['d.frequency_cap_mode'],
                'enabled':          db_result['d.enabled'],
                'inFlightStart':    to_iso_8601(db_result['d.in_flight_start']),
                'inFlightEnd':      to_iso_8601(db_result['d.in_flight_end']),
                'inFlightTimeZone': db_result['d.in_flight_time_zone'],
                'archived':         db_result['d.archived'],

                'targeting': {
                    'id':   db_result['t.id'],
                    'name': db_result['t.name'],

                    'filters': [
                        {
                            'type': 'geo',
                            'mode': db_result['t.geos_mode'],
                            'list': GeoModel.get_targeting_list(cursor, targeting_id)
                        },
                        {
                            'type': 'domain',
                            'mode': db_result['t.domains_mode'],
                            'list': DomainModel.get_targeting_list(cursor, targeting_id)
                        },
                        {
                            'type': 'publisher',
                            'mode': db_result['t.publishers_mode'],
                            'list': PublisherModel.get_targeting_list(cursor, targeting_id)
                        },
                        {
                            'type': 'platform',
                            'mode': db_result['t.platforms_mode'],
                            'list': PlatformModel.get_targeting_list(cursor, targeting_id)
                        },
                        {
                            'type': 'browser',
                            'mode': db_result['t.browsers_mode'],
                            'list': BrowserModel.get_targeting_list(cursor, targeting_id)
                        },
                        {
                            'type': 'os',
                            'mode': db_result['t.oss_mode'],
                            'list': OSSModel.get_targeting_list(cursor, targeting_id)
                        },
                        {
                            'type': 'device',
                            'mode': db_result['t.devices_mode'],
                            'list': DeviceModel.get_targeting_list(cursor, targeting_id)
                        },
                        {
                            'type': 'domainString',
                            'mode': db_result['t.domain_strings_mode'],
                            'list': DomainModel.get_string_targeting_list(cursor, targeting_id)
                        }
                    ],

                    'inFlightTimeMatrix': {
                        'zone': db_result['t.in_flight_time_matrix_time_zone'],
                        'mode': db_result['t.in_flight_time_matrix_mode'],
                        'list': TimeMatrixModel.get_targeting_ids_list(cursor, targeting_id)
                    }
                }
            }

        return result

    # ------------- #
    # Get Full List #
    # ------------- #
    @staticmethod
    def get_list(cursor, filters):
        sql = "SELECT \
               `id`, \
               `name`, \
               `description`, \
               `type`, \
               `url`, \
               `floorCPM`, \
               `reqTimeout`, \
               `requestsCap`, \
               `requestsCapMode`, \
               `viewsCap`, \
               `viewsCapMode`, \
               `frequencyCap`, \
               `frequencyCapMode`, \
               `enabled`, \
               `inFlightStart`, \
               `inFlightEnd`, \
               `inFlightTimeZone`, \
               `targeting_id`, \
               `archived` \
               FROM `demand_source`"

        ### <filters> ###

        where = []
        replace = {}

        if 'archived' in filters.keys() \
        and filters['archived'] != None:
            where.append("`archived` = $archived")
            replace['archived'] = filters['archived']

        if 'search' in filters.keys() \
        and filters['search'] != None:
            where.append("`name` LIKE $search")
            replace['search'] = '%' + str(filters['search']) + '%'

        if len(where) > 0:
            sql += ' WHERE '
            sql += ' AND '.join(where)
            
        sql = sql_replace(sql, replace)

        ### </filters> ###

        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            result.append({
               'id':               db_item['id'],
               'name':             db_item['name'],
               'description':      db_item['description'],
               'type':             db_item['type'],
               'url':              db_item['url'],
               'floorCPM':         db_item['floorCPM'],
               'reqTimeout':       db_item['reqTimeout'],
               'requestsCap':      db_item['requestsCap'],
               'requestsCapMode':  db_item['requestsCapMode'],
               'viewsCap':         db_item['viewsCap'],
               'viewsCapMode':     db_item['viewsCapMode'],
               'frequencyCap':     db_item['frequencyCap'],
               'frequencyCapMode': db_item['frequencyCapMode'],
               'enabled':          db_item['enabled'],
               'inFlightStart':    to_iso_8601(db_item['inFlightStart']),
               'inFlightEnd':      to_iso_8601(db_item['inFlightEnd']),
               'inFlightTimeZone': db_item['inFlightTimeZone'],
               'targetingId':      db_item['targeting_id'],
               'archived':         db_item['archived']
            })

        return result

    # ------------------------- #
    # Get Related With Tier Ids #
    # ------------------------- #
    @staticmethod
    def get_tier_relation(cursor, tier_id):
        sql = "SELECT `demand_source_id` \
               FROM `rel_tier_source` \
               WHERE `demand_source_tier_id` = $tier_id"

        replace = dict(tier_id=tier_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            result.append(int(db_item['demand_source_id']))

        result.sort()

        if result == None:
            result = []

        return result


    # ----------- #
    # Insert Data #
    # ----------- #
    @staticmethod
    def create(cursor, data):
        demand_source_id = None

        ### Step[1]: Add Targeting
        targeting = {}
        targeting_filters = data['targeting']['filters']
        targeting_names = ['geo',
                           'domain', 
                           'publisher', 
                           'platform',
                           'browser',
                           'os',
                           'device',
                           'domainString']

        for targeting_filter in targeting_filters:
            if 'type' in targeting_filter.keys():
                targeting[targeting_filter['type']] = {
                    'mode': targeting_filter['mode'], 
                    'list': targeting_filter['list']
                }

        for targeting_name in targeting_names:
            if targeting_name not in targeting.keys():
                targeting[targeting_name] = {
                    'mode': -1, 
                    'list': []
                }

        # Dat for check targeting
        targeting_data = {
            'name': '',
            'geosMode': str(targeting['geo']['mode']),
            'domainsMode': str(targeting['domain']['mode']),
            'publishersMode': str(targeting['publisher']['mode']),
            'platformsMode': str(targeting['platform']['mode']),
            'browsersMode': str(targeting['browser']['mode']),
            'ossMode': str(targeting['os']['mode']),
            'devicesMode': str(targeting['device']['mode']),
            'domainStringsMode': str(targeting['domainString']['mode']),
            'inFlightTimeMatrixTimeZone': str(0),
            'inFlightTimeMatrixMode': str(1),
            'filters': {
                'geo': targeting['geo']['list'],
                'domain': targeting['domain']['list'],
                'publisher': targeting['publisher']['list'],
                'platform': targeting['platform']['list'],
                'browser': targeting['browser']['list'],
                'os': targeting['os']['list'],
                'device': targeting['device']['list'],
                'domainString': targeting['domainString']['list'],
            },
            'matrix': []
        }

        time_matrix = data['targeting']['inFlightTimeMatrix']['list']
        for time_interval in time_matrix:
            targeting_data['matrix'].append({
                'dayId': time_interval['dayId'],
                'startTimeId': time_interval['startTimeId'],
                'endTimeId': time_interval['endTimeId']
            })

        # Check if is tergeting duplicate
        targeting_id = TargetingModel.check(cursor, targeting_data)

        if targeting_id == None:
            # Dat for targeting model
            targeting_data = {
                'name': '',
                'geosMode': str(targeting['geo']['mode']),
                'domainsMode': str(targeting['domain']['mode']),
                'publishersMode': str(targeting['publisher']['mode']),
                'platformsMode': str(targeting['platform']['mode']),
                'browsersMode': str(targeting['browser']['mode']),
                'ossMode': str(targeting['os']['mode']),
                'devicesMode': str(targeting['device']['mode']),
                'domainStringsMode': str(targeting['domainString']['mode']),
                'inFlightTimeMatrixTimeZone': str(0),
                'inFlightTimeMatrixMode': str(1)
            }

            # Create targeting
            targeting_id = TargetingModel.create(cursor, targeting_data)

            # Return if no targeting
            if targeting_id == None:
                return None

            # Create geo relation
            for item_id in targeting['geo']['list']:
                GeoModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create domain relation
            for item_id in targeting['domain']['list']:
                DomainModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create publisher relation
            for item_id in targeting['publisher']['list']:
                PublisherModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create platform relation
            for item_id in targeting['platform']['list']:
                PlatformModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create browser relation
            for item_id in targeting['browser']['list']:
                BrowserModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create oss relation
            for item_id in targeting['os']['list']:
                OSSModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create device relation
            for item_id in targeting['device']['list']:
                DeviceModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create string domain and relation
            for domain in targeting['domainString']['list']:
                DomainModel.create_string_targeting_relation(cursor, domain, targeting_id)

            # Create time matrix relation
            time_matrix = data['targeting']['inFlightTimeMatrix']['list']
            for time_interval in time_matrix:
                TimeMatrixModel.create_targeting_relation(cursor,
                                                          time_interval['dayId'],
                                                          time_interval['startTimeId'],
                                                          time_interval['endTimeId'],
                                                          targeting_id)

        ### Step[2]: Add Demand Source
        sql = "INSERT INTO `demand_source` ( \
               `name`, \
               `description`, \
               `type`, \
               `url`, \
               `floorCPM`, \
               `reqTimeout`, \
               `requestsCap`, \
               `requestsCapMode`, \
               `viewsCap`, \
               `viewsCapMode`, \
               `frequencyCap`, \
               `frequencyCapMode`, \
               `enabled`, \
               `inFlightStart`, \
               `inFlightEnd`, \
               `inFlightTimeZone`, \
               `targeting_id`, \
               `archived` \
               ) VALUES ( \
               $name, \
               $description, \
               $type, \
               $url, \
               $floorCPM, \
               $reqTimeout, \
               $requestsCap, \
               $requestsCapMode, \
               $viewsCap, \
               $viewsCapMode, \
               $frequencyCap, \
               $frequencyCapMode, \
               $enabled, \
               $inFlightStart, \
               $inFlightEnd, \
               $inFlightTimeZone, \
               $targetingId, \
               $archived \
               )"

        replace = dict(name=data['name'],
                       description=data['description'],
                       type=data['type'],
                       url=data['url'],
                       floorCPM=data['floorCPM'],
                       reqTimeout=data['reqTimeout'],
                       requestsCap=data['requestsCap'],
                       requestsCapMode=data['requestsCapMode'],
                       viewsCap=data['viewsCap'],
                       viewsCapMode=data['viewsCapMode'],
                       frequencyCap=data['frequencyCap'],
                       frequencyCapMode=data['frequencyCapMode'],
                       enabled=data['enabled'],
                       inFlightStart=from_iso_8601(data['inFlightStart']),
                       inFlightEnd=from_iso_8601(data['inFlightEnd']),
                       inFlightTimeZone=data['inFlightTimeZone'],
                       targetingId=targeting_id,
                       archived=data['archived'])

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        demand_source_id = cursor.lastrowid

        return demand_source_id

    # ---------- #
    # Copy By Id #
    # ---------- #
    @staticmethod
    def duplicate(cursor, id):
        demand_source_id = None

        sql = "SELECT \
               `name`, \
               `description`, \
               `type`, \
               `url`, \
               `floorCPM`, \
               `reqTimeout`, \
               `requestsCap`, \
               `requestsCapMode`, \
               `viewsCap`, \
               `viewsCapMode`, \
               `frequencyCap`, \
               `frequencyCapMode`, \
               `enabled`, \
               `inFlightStart`, \
               `inFlightEnd`, \
               `inFlightTimeZone`, \
               `targeting_id`, \
               `archived` \
               FROM `demand_source` \
               WHERE `id` = $demand_source_id"

        replace = dict(demand_source_id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        original_demand_source = cursor.fetchone()

        if original_demand_source == None:
            return None

        sql = "INSERT INTO `demand_source` ( \
               `name`, \
               `description`, \
               `type`, \
               `url`, \
               `floorCPM`, \
               `reqTimeout`, \
               `requestsCap`, \
               `requestsCapMode`, \
               `viewsCap`, \
               `viewsCapMode`, \
               `frequencyCap`, \
               `frequencyCapMode`, \
               `enabled`, \
               `inFlightStart`, \
               `inFlightEnd`, \
               `inFlightTimeZone`, \
               `targeting_id`, \
               `archived` \
               ) VALUES ( \
               $name, \
               $description, \
               $type, \
               $url, \
               $floorCPM, \
               $reqTimeout, \
               $requestsCap, \
               $requestsCapMode, \
               $viewsCap, \
               $viewsCapMode, \
               $frequencyCap, \
               $frequencyCapMode, \
               $enabled, \
               $inFlightStart, \
               $inFlightEnd, \
               $inFlightTimeZone, \
               $targetingId, \
               $archived \
               )"

        replace = dict(name=original_demand_source['name'],
                       description=original_demand_source['description'],
                       type=original_demand_source['type'],
                       url=original_demand_source['url'],
                       floorCPM=original_demand_source['floorCPM'],
                       reqTimeout=original_demand_source['reqTimeout'],
                       requestsCap=original_demand_source['requestsCap'],
                       requestsCapMode=original_demand_source['requestsCapMode'],
                       viewsCap=original_demand_source['viewsCap'],
                       viewsCapMode=original_demand_source['viewsCapMode'],
                       frequencyCap=original_demand_source['frequencyCap'],
                       frequencyCapMode=original_demand_source['frequencyCapMode'],
                       enabled=original_demand_source['enabled'],
                       inFlightStart=original_demand_source['inFlightStart'],
                       inFlightEnd=original_demand_source['inFlightEnd'],
                       inFlightTimeZone=original_demand_source['inFlightTimeZone'],
                       targetingId=original_demand_source['targeting_id'],
                       archived=original_demand_source['archived'])
        
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        demand_source_id = cursor.lastrowid

        return demand_source_id


    # ---------------- #
    # Relate With Tier #
    # ---------------- #
    @staticmethod
    def create_tier_relation(cursor, demand_source_id, tier_id):
        relation_id = None

        sql = "INSERT INTO `rel_tier_source` \
               (`demand_source_id`, `demand_source_tier_id`) \
               VALUES ($demand_source_id, $tier_id)"

        replace = dict(demand_source_id=demand_source_id, 
                       tier_id=tier_id)

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        relation_id = cursor.lastrowid

        return relation_id

    # ----------- #
    # Update Data #
    # ----------- #
    @staticmethod
    def update(cursor, id, data):
        demand_source_id = None

        ### Step[1]: Add Targeting
        targeting = {}
        targeting_filters = data['targeting']['filters']
        targeting_names = ['geo',
                           'domain', 
                           'publisher', 
                           'platform',
                           'browser',
                           'os',
                           'device',
                           'domainString']

        for targeting_filter in targeting_filters:
            if 'type' in targeting_filter.keys():
                targeting[targeting_filter['type']] = {
                    'mode': targeting_filter['mode'], 
                    'list': targeting_filter['list']
                }

        for targeting_name in targeting_names:
            if targeting_name not in targeting.keys():
                targeting[targeting_name] = {
                    'mode': -1, 
                    'list': []
                }

        # Dat for check targeting
        targeting_data = {
            'name': '',
            'geosMode': str(targeting['geo']['mode']),
            'domainsMode': str(targeting['domain']['mode']),
            'publishersMode': str(targeting['publisher']['mode']),
            'platformsMode': str(targeting['platform']['mode']),
            'browsersMode': str(targeting['browser']['mode']),
            'ossMode': str(targeting['os']['mode']),
            'devicesMode': str(targeting['device']['mode']),
            'domainStringsMode': str(targeting['domainString']['mode']),
            'inFlightTimeMatrixTimeZone': str(0),
            'inFlightTimeMatrixMode': str(1),
            'filters': {
                'geo': targeting['geo']['list'],
                'domain': targeting['domain']['list'],
                'publisher': targeting['publisher']['list'],
                'platform': targeting['platform']['list'],
                'browser': targeting['browser']['list'],
                'os': targeting['os']['list'],
                'device': targeting['device']['list'],
                'domainString': targeting['domainString']['list'],
            },
            'matrix': []
        }

        time_matrix = data['targeting']['inFlightTimeMatrix']['list']
        for time_interval in time_matrix:
            targeting_data['matrix'].append({
                'dayId': time_interval['dayId'],
                'startTimeId': time_interval['startTimeId'],
                'endTimeId': time_interval['endTimeId']
            })

        # Check if is tergeting duplicate
        targeting_id = TargetingModel.check(cursor, targeting_data)

        if targeting_id == None:
            # Data for targeting model
            targeting_data = {
                'name': '',
                'geosMode': str(targeting['geo']['mode']),
                'domainsMode': str(targeting['domain']['mode']),
                'publishersMode': str(targeting['publisher']['mode']),
                'platformsMode': str(targeting['platform']['mode']),
                'browsersMode': str(targeting['browser']['mode']),
                'ossMode': str(targeting['os']['mode']),
                'devicesMode': str(targeting['device']['mode']),
                'domainStringsMode': str(targeting['domainString']['mode']),
                'inFlightTimeMatrixTimeZone': str(0),
                'inFlightTimeMatrixMode': str(1)
            }

            # Create targeting
            targeting_id = TargetingModel.create(cursor, targeting_data)

            # Return if no targeting
            if targeting_id == None:
                return None

            # Create geo relation
            for item_id in targeting['geo']['list']:
                GeoModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create domain relation
            for item_id in targeting['domain']['list']:
                DomainModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create publisher relation
            for item_id in targeting['publisher']['list']:
                PublisherModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create platform relation
            for item_id in targeting['platform']['list']:
                PlatformModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create browser relation
            for item_id in targeting['browser']['list']:
                BrowserModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create oss relation
            for item_id in targeting['os']['list']:
                OSSModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create device relation
            for item_id in targeting['device']['list']:
                DeviceModel.create_targeting_relation(cursor, item_id, targeting_id)

            # Create string domain and relation
            for domain in targeting['domainString']['list']:
                DomainModel.create_string_targeting_relation(cursor, domain, targeting_id)

            # Create time matrix relation
            time_matrix = data['targeting']['inFlightTimeMatrix']['list']
            for time_interval in time_matrix:
                TimeMatrixModel.create_targeting_relation(cursor,
                                                          time_interval['dayId'],
                                                          time_interval['startTimeId'],
                                                          time_interval['endTimeId'],
                                                          targeting_id)

        ### Step[2]: Update Demand Source
        sql = "SELECT `targeting_id` \
               FROM `demand_source` \
               WHERE `id` = $id"

        replace = dict(id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchone()
        old_targeting_id = None

        if db_result != None:
            old_targeting_id = db_result['targeting_id']

        sql = "UPDATE `demand_source` SET \
               `name` = $name, \
               `description` = $description, \
               `type` = $type, \
               `url` = $url, \
               `floorCPM` = $floorCPM, \
               `reqTimeout` = $reqTimeout, \
               `requestsCap` = $requestsCap, \
               `requestsCapMode` = $requestsCapMode, \
               `viewsCap` = $viewsCap, \
               `viewsCapMode` = $viewsCapMode, \
               `frequencyCap` = $frequencyCap, \
               `frequencyCapMode` = $frequencyCapMode, \
               `enabled` = $enabled, \
               `inFlightStart` = $inFlightStart, \
               `inFlightEnd` = $inFlightEnd, \
               `inFlightTimeZone` = $inFlightTimeZone, \
               `targeting_id` = $targetingId, \
               `archived` = $archived \
               WHERE `id` = $id"

        replace = dict(name=data['name'],
                       description=data['description'],
                       type=data['type'],
                       url=data['url'],
                       floorCPM=data['floorCPM'],
                       reqTimeout=data['reqTimeout'],
                       requestsCap=data['requestsCap'],
                       requestsCapMode=data['requestsCapMode'],
                       viewsCap=data['viewsCap'],
                       viewsCapMode=data['viewsCapMode'],
                       frequencyCap=data['frequencyCap'],
                       frequencyCapMode=data['frequencyCapMode'],
                       enabled=data['enabled'],
                       inFlightStart=from_iso_8601(data['inFlightStart']),
                       inFlightEnd=from_iso_8601(data['inFlightEnd']),
                       inFlightTimeZone=data['inFlightTimeZone'],
                       targetingId=targeting_id,
                       archived=data['archived'],
                       id=id)

        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        if old_targeting_id != None:
            TargetingModel.delete_demand_source_relation(cursor, old_targeting_id)

        demand_source_id = int(id)

        return demand_source_id

    # -------------- #
    # Update Archive #
    # -------------- #
    @staticmethod
    def update_archive(cursor, id, archived):
        result = None

        sql = "UPDATE `demand_source` \
               SET `archived` = $archived \
               WHERE `id` = $id"

        replace = dict(id=id, archived=archived)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = int(id)

        return result

    # -------------- #
    # Update Enabled #
    # -------------- #
    @staticmethod
    def update_enable(cursor, id, enabled):
        result = None

        sql = "UPDATE `demand_source` \
               SET `enabled` = $enabled \
               WHERE `id` = $id"

        replace = dict(id=id, enabled=enabled)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = int(id)

        return result