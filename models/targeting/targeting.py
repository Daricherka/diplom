from ..functions import *
from geo import *
from domain import *
from publisher import *
from platform import *
from browser import *
from os import *
from device import *
from ..matrix import *


##################
### Targeting  ###
##################
class TargetingModel(object):
    # ------------------------- #
    # Check If Targeting Exists #
    # ------------------------- #
    @staticmethod
    def check(cursor, data):
        targeting_id = None

        sql = "SELECT `id` \
               FROM `targeting` \
               WHERE `name` = $name \
               AND `geosMode` = $geosMode \
               AND `domainsMode` = $domainsMode \
               AND `publishersMode` = $publishersMode \
               AND `platformsMode` = $platformsMode \
               AND `browsersMode` = $browsersMode \
               AND `ossMode` = $ossMode \
               AND `devicesMode` = $devicesMode \
               AND `domainStringsMode` = $domainStringsMode \
               AND `inFlightTimeMatrixTimeZone` = $inFlightTimeMatrixTimeZone \
               AND `inFlightTimeMatrixMode` = $inFlightTimeMatrixMode"

        replace = dict(name=data['name'], 
                       geosMode=data['geosMode'],
                       domainsMode=data['domainsMode'],
                       publishersMode=data['publishersMode'],
                       platformsMode=data['platformsMode'],
                       browsersMode=data['browsersMode'],
                       ossMode=data['ossMode'],
                       devicesMode=data['devicesMode'],
                       domainStringsMode=data['domainStringsMode'],
                       inFlightTimeMatrixTimeZone=data['inFlightTimeMatrixTimeZone'],
                       inFlightTimeMatrixMode=data['inFlightTimeMatrixMode'])

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()

        if len(db_result) == 0:
            return None

        filters = {
            'geo': [],
            'domain': [],
            'publisher': [],
            'platform': [],
            'browser': [],
            'os': [],
            'device': [],
            'domainString': []
        }

        for key in filters.keys():
            if key == 'domainString':
                for item in data['filters'][key]:
                    filters[key].append(str(item))

            else:
                for item in data['filters'][key]:
                    filters[key].append(int(item))

            filters[key].sort()

            if filters[key] == None:
                filters[key] = []

        matrix = []

        for interval in data['matrix']:
            d = str(interval['dayId'])
            s = str(interval['startTimeId'])
            e = str(interval['endTimeId'])
            matrix.append(d + '|' + s + '|' + e)

        matrix.sort()

        if matrix == None:
            matrix = []

        for db_item in db_result:
            if filters['geo'] != GeoModel.get_targeting_relation(cursor, db_item['id']):
                continue

            if filters['domain'] != DomainModel.get_targeting_relation(cursor, db_item['id']):
                continue

            if filters['publisher'] != PublisherModel.get_targeting_relation(cursor, db_item['id']):
                continue

            if filters['platform'] != PlatformModel.get_targeting_relation(cursor, db_item['id']):
                continue

            if filters['browser'] != BrowserModel.get_targeting_relation(cursor, db_item['id']):
                continue

            if filters['os'] != OSSModel.get_targeting_relation(cursor, db_item['id']):
                continue

            if filters['device'] != DeviceModel.get_targeting_relation(cursor, db_item['id']):
                continue

            if filters['domainString'] != DomainModel.get_string_targeting_relation(cursor, db_item['id']):
                continue

            if matrix != TimeMatrixModel.get_targeting_relation(cursor, db_item['id']):
                continue

            targeting_id = db_item['id']
            break

        return targeting_id

    # ----------- #
    # Insert Data #
    # ----------- #
    @staticmethod
    def create(cursor, data):
        targeting_id = None
        replace = data

        sql = "INSERT INTO `targeting` ( \
               `name`, \
               `geosMode`, \
               `domainsMode`, \
               `publishersMode`, \
               `platformsMode`, \
               `browsersMode`, \
               `ossMode`, \
               `devicesMode`, \
               `domainStringsMode`, \
               `inFlightTimeMatrixTimeZone`, \
               `inFlightTimeMatrixMode` \
               ) VALUES ( \
               $name, \
               $geosMode, \
               $domainsMode, \
               $publishersMode, \
               $platformsMode, \
               $browsersMode, \
               $ossMode, \
               $devicesMode, \
               $domainStringsMode, \
               $inFlightTimeMatrixTimeZone, \
               $inFlightTimeMatrixMode)"

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        targeting_id = cursor.lastrowid

        return targeting_id

    # ------ #
    # Delete #
    # ------ #
    @staticmethod
    def delete_demand_source_relation(cursor, targeting_id=None):
        if targeting_id == None:
            return False

        sql = "SELECT `id` \
               FROM `demand_source` \
               WHERE `targeting_id` = $targeting_id \
               LIMIT 1"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()

        if len(db_result) > 0:
            return False

        GeoModel.delete_targeting_relation(cursor, targeting_id)
        DomainModel.delete_targeting_relation(cursor, targeting_id)
        PublisherModel.delete_targeting_relation(cursor, targeting_id)
        PlatformModel.delete_targeting_relation(cursor, targeting_id)
        BrowserModel.delete_targeting_relation(cursor, targeting_id)
        OSSModel.delete_targeting_relation(cursor, targeting_id)
        DeviceModel.delete_targeting_relation(cursor, targeting_id)
        TimeMatrixModel.delete_targeting_relation(cursor, targeting_id)
        DomainModel.delete_string_targeting_relation(cursor, targeting_id)

        sql = "DELETE FROM `targeting` \
               WHERE `id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return True        
