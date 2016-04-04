from functions import *
from tier import *
from source import *


################
### Scenario ###
################
class ScenarioModel(object):
    # ---------- #
    # Count Rows #
    # ---------- #
    @staticmethod
    def get_count(cursor):
        sql = "SELECT \
               count(`id`) AS `count` \
               FROM `demand_source_scenario`"

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
               `s`.`id` AS `s.id`, \
               `s`.`name` AS `s.name`, \
               `s`.`description` AS `s.description`, \
               `s`.`archived` AS `s.archived`, \
               `t`.`id` AS `t.id`, \
               `t`.`name` AS `t.name`, \
               `t`.`order` AS `t.order`, \
               `t`.`timeout` AS `t.timeout`, \
               `t`.`archived` AS `t.archived`, \
               `d`.`id` AS `d.id`, \
               `d`.`name` AS `d.name`, \
               `d`.`enabled` AS `d.enabled` \
               FROM `demand_source_scenario` AS `s` \
               LEFT JOIN `rel_tier_scenario` AS `st` \
                   LEFT JOIN `demand_source_tier` AS `t` \
                       LEFT JOIN rel_tier_source AS `td` \
                           LEFT JOIN `demand_source` AS `d` \
                           ON `td`.`demand_source_id` = `d`.`id` \
                       ON `t`.`id` = `td`.`demand_source_tier_id` \
                   ON `st`.`demand_source_tier_id` = `t`.`id` \
               ON `s`.`id` = st.`demand_source_scenario_id` \
               WHERE `s`.`id` = $id"

        replace = dict(id=str(id))
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()

        if len(db_result) == 0:
            return None

        result = {}
        if len(db_result) > 0:
            result = {
                'id':          db_result[0]['s.id'], 
                'name':        db_result[0]['s.name'],
                'description': db_result[0]['s.description'],
                'archived':    db_result[0]['s.archived'],
                'tiers':       []
            }

            for db_item in db_result:
                if db_item['t.id'] == None:
                    continue

                tier_exists = False
                for tier in result['tiers']:
                    if tier['id'] == db_item['t.id']:
                        tier_exists = True
                        break

                if not tier_exists:
                    result['tiers'].append({
                        'id':            db_item['t.id'],
                        'name':          db_item['t.name'],
                        'order':         db_item['t.order'],
                        'timeout':       db_item['t.timeout'],
                        'archived':      db_item['t.archived'],
                        'demandSources': []
                    })

                for tier in result['tiers']:
                    if tier['id'] == db_item['t.id']:
                        if db_item['d.id'] != None:
                            tier['demandSources'].append({
                                'id':      db_item['d.id'],
                                'name':    db_item['d.name'],
                                'enabled': db_item['d.enabled']
                            })
                            break

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
               `archived` \
               FROM `demand_source_scenario`"

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
               'id':          db_item['id'],
               'name':        db_item['name'],
               'description': db_item['description'],
               'archived':    db_item['archived']
            })

        return result

    # ----------- #
    # Insert Data #
    # ----------- #
    @staticmethod
    def create(cursor, data):
        scenario_id = None
        ### Step[1]: Add Scenario
        sql = "INSERT INTO `demand_source_scenario` \
               (`name`,  `description`, `archived`) \
               VALUES ($name, $description, $archived)"

        replace = dict(name=str(data['name']), 
                       description=str(data['description']),
                       archived=str(0))

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        scenario_id = cursor.lastrowid

        ### Step[2]: Add Tiers
        for tier in data['tiers']:
            tier_id = None

            # Check tier data
            tier_data = {
                'order': str(tier['order']),
                'timeout': str(tier['timeout']),
                'demandSources': []
            }

            for demand_source_id in tier['demandSources']:
                tier_data['demandSources'].append(int(demand_source_id))

            tier_data['demandSources'].sort()
            
            if tier_data['demandSources'] == None:
                tier_data['demandSources'] = []

            # Check if tier exists
            tier_id = TierModel.check(cursor, tier_data)

            if tier_id != None:
                # Relate tier with scenario
                TierModel.create_scenario_relation(cursor, tier_id, scenario_id)
            else:
                # New tier data
                tier_data = {
                    'order': str(tier['order']),
                    'timeout': str(tier['timeout'])
                }

                # Create new tier
                tier_id = TierModel.create(cursor, tier_data)

                # Relate tier with scenario
                TierModel.create_scenario_relation(cursor, tier_id, scenario_id)

                ### Step[3]: Add Demand Sources
                for demand_source_id in tier['demandSources']:
                    # Relate demand source with tier
                    DemandSourceModel.create_tier_relation(cursor, demand_source_id, tier_id)

        return scenario_id

    # ---------- #
    # Copy By Id #
    # ---------- #
    @staticmethod
    def duplicate(cursor, id):
        scenario_id = None

        ### Step[1]: Add Scenario
        sql = "SELECT \
               `name`, \
               `description`, \
               `archived` \
               FROM `demand_source_scenario` \
               WHERE `id` = $id"

        replace = dict(id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        original_scenario = cursor.fetchone()

        if original_scenario == None:
            return None

        sql = "INSERT INTO `demand_source_scenario` \
               (`name`, `description`, `archived`) \
               VALUES ($name, $description, $archived)"

        replace = dict(name=original_scenario['name'],
                       description=original_scenario['description'],
                       archived=original_scenario['archived'])

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        scenario_id = cursor.lastrowid

        ### Step[2]: Add Tier Relations
        related_tier_ids = TierModel.get_scenario_relation(cursor, id)

        for related_tier_id in related_tier_ids:
            TierModel.create_scenario_relation(cursor, related_tier_id, scenario_id)

        return scenario_id

    # ----------- #
    # Update Data #
    # ----------- #
    @staticmethod
    def update(cursor, id, data):
        scenario_id = id

        ### Step[1]: Update Scenario
        sql = "UPDATE `demand_source_scenario` SET \
               `name` = $name, \
               `description` = $description, \
               `archived` = $archived \
               WHERE `id` = $scenario_id"

        replace = dict(scenario_id=scenario_id,
                       name=data['name'],
                       description=data['description'],
                       archived=0)

        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        ### Step[2]: Delete Related Tiers
        TierModel.delete_scenario_relation(cursor, scenario_id)

        ### Step[3]: Add New Tiers
        for tier in data['tiers']:
            tier_id = None

            # Check tier data
            tier_data = {
                'order': str(tier['order']),
                'timeout': str(tier['timeout']),
                'demandSources': []
            }

            for demand_source_id in tier['demandSources']:
                tier_data['demandSources'].append(int(demand_source_id))

            tier_data['demandSources'].sort()

            if tier_data['demandSources'] == None:
                tier_data['demandSources'] = []

            # Check if tier exists
            tier_id = TierModel.check(cursor, tier_data)

            if tier_id != None:
                # Relate tier with scenario
                TierModel.create_scenario_relation(cursor, tier_id, scenario_id)
            else:
                # New tier data
                tier_data = {
                    'order': str(tier['order']),
                    'timeout': str(tier['timeout'])
                }

                # Create new tier
                tier_id = TierModel.create(cursor, tier_data)

                # Relate tier with scenario
                TierModel.create_scenario_relation(cursor, tier_id, scenario_id)

                ### Step[3]: Add Demand Sources
                for demand_source_id in tier['demandSources']:
                    # Relate demand source with tier
                    DemandSourceModel.create_tier_relation(cursor, demand_source_id, tier_id)

        return scenario_id

    # -------------- #
    # Update Archive #
    # -------------- #
    @staticmethod
    def update_archive(cursor, id, archived):
        result = None

        sql = "UPDATE `demand_source_scenario` \
               SET `archived` = $archived \
               WHERE `id` = $id"

        replace = dict(id=id, archived=archived)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = int(id)

        return result