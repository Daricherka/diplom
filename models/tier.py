from functions import *
from source import *


############
### Tier ###
############
class TierModel(object):
    # ---------- #
    # Count Rows #
    # ---------- #
    @staticmethod
    def get_count(cursor):
        sql = "SELECT \
               count(`id`) AS `count` \
               FROM `demand_source_tier`"

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
               `id`, \
               `name`, \
               `order`, \
               `timeout`, \
               `archived` \
               FROM `demand_source_tier` \
               WHERE `id` = $id"

        replace = dict(id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchone()
        result = {}

        if db_result != None:
            result = {
               'id':       db_result['id'],
               'name':     db_result['name'],
               'order':    db_result['order'],
               'timeout':  db_result['timeout'],
               'archived': db_result['archived']
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
               `order`, \
               `timeout`, \
               `archived` \
               FROM `demand_source_tier`"

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
               'id':       db_item['id'],
               'name':     db_item['name'],
               'order':    db_item['order'],
               'timeout':  db_item['timeout'],
               'archived': db_item['archived']
            })

        return result

    # ----------------------------- #
    # Get Related With Scenario Ids #
    # ----------------------------- #
    @staticmethod
    def get_scenario_relation(cursor, scenario_id):
        sql = "SELECT `demand_source_tier_id` \
               FROM `rel_tier_scenario` \
               WHERE `demand_source_scenario_id` = $scenario_id"

        replace = dict(scenario_id=scenario_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            result.append(int(db_item['demand_source_tier_id']))

        result.sort()

        if result == None:
            result = []

        return result

    # -------------------- #
    # Check If Tier Exists #
    # -------------------- #
    @staticmethod
    def check(cursor, data):
        tier_id = None

        sql = "SELECT `id` \
               FROM `demand_source_tier` \
               WHERE `order` = $order \
               AND `timeout` = $timeout"

        replace = dict(order=data['order'], 
                       timeout=data['timeout'])

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()

        if len(db_result) == 0:
            return None

        for db_item in db_result:
            demand_sources = DemandSourceModel.get_tier_relation(cursor, db_item['id'])
            if demand_sources == data['demandSources']:
                tier_id = db_item['id']
                break

        return tier_id

    # ----------- #
    # Insert Data #
    # ----------- #
    @staticmethod
    def create(cursor, data):
        tier_id = None
        replace = data

        sql = "INSERT INTO `demand_source_tier` \
               (`order`, `timeout`) \
               VALUES ($order, $timeout)"

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        tier_id = cursor.lastrowid

        return tier_id

    # -------------------- #
    # Relate With Scenario #
    # -------------------- #
    @staticmethod
    def create_scenario_relation(cursor, tier_id, scenario_id):
        relation_id = None

        sql = "INSERT INTO `rel_tier_scenario` \
               (`demand_source_scenario_id`, `demand_source_tier_id`) \
               VALUES ($scenario_id, $tier_id)"

        replace = dict(scenario_id=scenario_id, 
                       tier_id=tier_id)

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        relation_id = cursor.lastrowid

        return relation_id

    # -------------- #
    # Update Archive #
    # -------------- #
    @staticmethod
    def update_archive(cursor, id, archived):
        result = None

        sql = "UPDATE `demand_source_tier` \
               SET `archived` = $archived \
               WHERE `id` = $id"

        replace = dict(id=id, archived=archived)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = int(id)

        return result

    # ---------------------------- #
    # Delete Related With Scenario #
    # ---------------------------- #
    @staticmethod
    def delete_scenario_relation(cursor, scenario_id):
        sql = "SELECT `demand_source_tier_id` \
               FROM `rel_tier_scenario` \
               WHERE `demand_source_scenario_id` = $scenario_id"

        replace = dict(scenario_id=scenario_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()

        if len(db_result) > 0:
            sql = "DELETE FROM `rel_tier_scenario` \
                   WHERE `demand_source_scenario_id` = $scenario_id"

            replace = dict(scenario_id=scenario_id)
            sql = sql_replace(sql, replace)
            cursor.execute(sql)

        for db_item in db_result:
            sql = "SELECT count(`id`) AS `count` \
                   FROM `rel_tier_scenario` \
                   WHERE `demand_source_tier_id` = $tier_id"

            replace = dict(tier_id=db_item['demand_source_tier_id'])
            sql = sql_replace(sql, replace)
            cursor.execute(sql)
            tier_db_result = cursor.fetchone()
            count = 0

            if tier_db_result != None:
                count = int(tier_db_result['count'])

            if count == 0:
                sql = "DELETE FROM `rel_tier_source` \
                       WHERE `demand_source_tier_id` = $tier_id"

                replace = dict(tier_id=db_item['demand_source_tier_id'])
                sql = sql_replace(sql, replace)
                cursor.execute(sql)

                sql = "DELETE FROM `demand_source_tier` \
                       WHERE `id` = $tier_id"

                replace = dict(tier_id=db_item['demand_source_tier_id'])
                sql = sql_replace(sql, replace)
                cursor.execute(sql)

        return True