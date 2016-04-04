from ..functions import *


##############
### Domain ###
##############
class DomainModel(object):
    # --------------------- #
    # Count Domains In List #
    # --------------------- #
    @staticmethod
    def count_domains(cursor, list_id):
        sql = "SELECT \
               count(`id`) AS `count` \
               FROM `rel_domain_pack_domain` \
               WHERE `domain_pack_id` = $list_id"

        replace = dict(list_id=list_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = cursor.fetchone()

        if result != None:
            return result['count']
        return 0

    # --------- #
    # Get By Id #
    # --------- #
    @staticmethod
    def get(cursor, id):
        sql = "SELECT \
               `p`.`id` AS `p.id`, \
               `p`.`name` AS `p.name`, \
               `p`.`description` AS `p.description`, \
               `p`.`archived` AS `p.archived`, \
               `l`.`id` AS `l.id`, \
               `l`.`domain` AS `l.domain` \
               FROM `domain_pack` AS `p` \
               LEFT JOIN `rel_domain_pack_domain` AS `r` \
                    LEFT JOIN `list_domain` AS `l` \
                    ON `r`.`list_domain_id` = `l`.`id` \
               ON `p`.`id` = `r`.`domain_pack_id` \
               WHERE `p`.`id` = $id"

        replace = dict(id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = {}

        if len(db_result) > 0:
            result = {
                'id':          db_result[0]['p.id'],
                'name':        db_result[0]['p.name'],
                'description': db_result[0]['p.description'],
                'archived':    db_result[0]['p.archived'],
                'domains':     []
            }

            for db_item in db_result:
                if db_item['l.domain'] != None:
                    result['domains'].append(db_item['l.domain'])

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
               FROM `domain_pack`"

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
                'id':           db_item['id'],
                'name':         db_item['name'],
                'description':  db_item['description'],
                'archived':     db_item['archived'],
                'domainsCount': DomainModel.count_domains(cursor, db_item['id'])
            })

        return result

    # ------------------- #
    # Get Full List (old) #
    # ------------------- #
    @staticmethod
    def old_get_list(cursor, filters):
        sql = "SELECT \
               `p`.`id` AS `p.id`, \
               `p`.`name` AS `p.name`, \
               `p`.`description` AS `p.description`, \
               `p`.`archived` AS `p.archived`, \
               `l`.`id` AS `l.id`, \
               `l`.`domain` AS `l.domain` \
               FROM `domain_pack` AS `p` \
               LEFT JOIN `rel_domain_pack_domain` AS `r` \
                    LEFT JOIN `list_domain` AS `l` \
                    ON `r`.`list_domain_id` = `l`.`id` \
               ON `p`.`id` = `r`.`domain_pack_id`"

        ### <filters> ###

        where = []
        replace = {}

        if 'archived' in filters.keys() \
        and filters['archived'] != None:
            where.append("`p`.`archived` = $archived")
            replace['archived'] = filters['archived']

        if 'search' in filters.keys() \
        and filters['search'] != None:
            where.append("`p`.`name` LIKE $search")
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
            item_exists = False

            for item in result:
                if item['id'] == db_item['p.id']:
                    item['domains'].append({
                        'id':   db_item['l.id'],
                        'name': db_item['l.domain']
                    })
                    item_exists = True
                    break

            if not item_exists:
                result.append({
                    'id':          db_item['p.id'],
                    'name':        db_item['p.name'],
                    'description': db_item['p.description'],
                    'archived':    db_item['p.archived'],

                    'domains': [{
                        'id':   db_item['l.id'],
                        'name': db_item['l.domain']
                    }]
                })

        return result

    # ------------------ #
    # Get List By Search #
    # ------------------ #
    @staticmethod
    def get_search_list(cursor, search):
        sql = "SELECT \
               `id` AS `id`, \
               `name` AS `value`, \
               `description` AS `description`, \
               `archived` AS `archived` \
               FROM `domain_pack` \
               WHERE `name` LIKE $search"

        replace = dict(search=str(search) + '%')
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return cursor.fetchall()

    # ------------------------ #
    # Get List By Targeting Id #
    # ------------------------ #
    @staticmethod
    def get_targeting_list(cursor, targeting_id):
        sql = "SELECT \
               `list`.`id` AS `id`, \
               `list`.`name` AS `value`, \
               `list`.`description` AS `description`, \
               `list`.`archived` AS `archived` \
               FROM `rel_domain_pack_targeting` AS `rel` \
               INNER JOIN `domain_pack` AS `list` \
               ON `rel`.`domain_pack_id` = `list`.`id` \
               WHERE `rel`.`targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return cursor.fetchall()

    # ------------------------------- #
    # Get Domain List By Targeting Id #
    # ------------------------------- #
    @staticmethod
    def get_string_targeting_list(cursor, targeting_id):
        sql = "SELECT \
               `list`.`id` AS `id`, \
               `list`.`domain` AS `value` \
               FROM `rel_domain` AS `rel` \
               INNER JOIN `list_domain` AS `list` \
               ON `rel`.`list_domain_id` = `list`.`id` \
               WHERE `rel`.`targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            result.append(db_item['value'])

        return result

    # ------------------------------ #
    # Get Related With Targeting Ids #
    # ------------------------------ #
    @staticmethod
    def get_targeting_relation(cursor, targeting_id):
        sql = "SELECT `domain_pack_id` \
               FROM `rel_domain_pack_targeting` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            result.append(int(db_item['domain_pack_id']))

        result.sort()

        if result == None:
            result = []

        return result

    # -------------------------------- #
    # Get Related With Targeting Names #
    # -------------------------------- #
    @staticmethod
    def get_string_targeting_relation(cursor, targeting_id):
        sql = "SELECT `list`.`domain` AS `value` \
               FROM `rel_domain` AS `rel` \
               INNER JOIN `list_domain` AS `list` \
               ON `rel`.`list_domain_id` = `list`.`id` \
               WHERE `rel`.`targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            result.append(str(db_item['value']))

        result.sort()

        if result == None:
            result = []

        return result

    # ---------------- #
    # Get Domain Names #
    # ---------------- #
    @staticmethod
    def get_domain_name_list(cursor, id):
        sql = "SELECT `l`.`domain` AS `domain` \
               FROM `list_domain` AS `l` \
               INNER JOIN `rel_domain_pack_domain` AS `r` \
               ON `l`.`id` = `r`.`list_domain_id` \
               WHERE `domain_pack_id` = $domain_pack_id"

        replace = dict(domain_pack_id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            result.append(db_item['domain'])

        return result

    # ------ #
    # Create #
    # ------ #
    @staticmethod
    def create(cursor, data):
        domain_pack_id = None

        sql = "INSERT INTO `domain_pack` \
               (`name`, `description`, `archived`) \
               VALUES ($name, $description, $archived)"

        replace = dict(name=data['name'],
                       description=data['description'],
                       archived=data['archived'])

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        domain_pack_id = cursor.lastrowid

        for domain_name in data['domains']:
            domain_id = None

            sql = "SELECT `id` \
                   FROM `list_domain` \
                   WHERE `domain` = $domain \
                   LIMIT 1"

            replace = dict(domain=domain_name)
            sql = sql_replace(sql, replace)
            cursor.execute(sql)
            db_result = cursor.fetchone()

            if db_result != None:
                domain_id = int(db_result['id'])

            if domain_id == None:
                sql = "INSERT INTO `list_domain` \
                       (`domain`) VALUES ($domain)"

                replace = dict(domain=domain_name)
                sql = sql_replace(sql, replace)
                cursor.execute(sql)
                domain_id = cursor.lastrowid

            sql = "INSERT INTO `rel_domain_pack_domain` \
                   (`domain_pack_id`, `list_domain_id`) \
                   VALUES ($domain_pack_id, $list_domain_id)"

            replace = dict(domain_pack_id=domain_pack_id,
                           list_domain_id=domain_id)

            sql = sql_replace(sql, replace)
            cursor.execute(sql)

        return domain_pack_id

    # ------------------------- #
    # Create Targeting Relation #
    # ------------------------- #
    @staticmethod
    def create_targeting_relation(cursor, id, targeting_id):
        sql = "INSERT INTO `rel_domain_pack_targeting` \
               (`domain_pack_id`, `targeting_id`) \
               VALUES ($id, $targeting_id)"

        replace = dict(id=id, targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return True

    # -------------------------------- #
    # Create String Targeting Relation #
    # -------------------------------- #
    @staticmethod
    def create_string_targeting_relation(cursor, domain, targeting_id):
        sql = "SELECT `id` \
               FROM `list_domain` \
               WHERE `domain` = $domain \
               LIMIT 1"

        replace = dict(domain=domain)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchone()
        list_domain_id = None

        if db_result == None:
            sql = "INSERT INTO `list_domain` \
                   (`domain`) VALUES ($domain)"

            replace = dict(domain=domain)
            sql = sql_replace(sql, replace)
            cursor.execute(sql)
            list_domain_id = cursor.lastrowid

        else:
            list_domain_id = int(db_result['id'])

        sql = "INSERT INTO `rel_domain` \
               (`list_domain_id`, `targeting_id`) \
               VALUES ($list_domain_id, $targeting_id)"

        replace = dict(list_domain_id=list_domain_id, 
                       targeting_id=targeting_id)

        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return True

    # ---- #
    # Copy #
    # ---- #
    @staticmethod
    def duplicate(cursor, id):
        domain_pack_id = None

        sql = "SELECT \
               `name`, \
               `description`, \
               `archived` \
               FROM `domain_pack` \
               WHERE `id` = $id"

        replace = dict(id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchone()

        if db_result == None:
            return None

        sql = "INSERT INTO `domain_pack` \
               (`name`, `description`, `archived`) \
               VALUES ($name, $description, $archived)"

        replace = dict(name=db_result['name'],
                       description=db_result['description'],
                       archived=db_result['archived'])

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        domain_pack_id = cursor.lastrowid

        sql = "SELECT `list_domain_id` \
               FROM `rel_domain_pack_domain` \
               WHERE `domain_pack_id` = $domain_pack_id"

        replace = dict(domain_pack_id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()

        for db_item in db_result:
            sql = "INSERT INTO `rel_domain_pack_domain` \
                   (`domain_pack_id`, `list_domain_id`) \
                   VALUES ($domain_pack_id, $list_domain_id)"

            replace = dict(domain_pack_id=domain_pack_id,
                           list_domain_id=db_item['list_domain_id'])

            sql = sql_replace(sql, replace)
            cursor.execute(sql)

        return domain_pack_id

    # ------ #
    # Update #
    # ------ #
    @staticmethod
    def update(cursor, id, data):
        domain_pack_id = None

        sql = "UPDATE `domain_pack` SET \
               `name` = $name, \
               `description` = $description, \
               `archived` = $archived \
               WHERE `id` = $id"

        replace = dict(name=data['name'],
                       description=data['description'],
                       archived=data['archived'],
                       id=id)

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        domain_pack_id = int(id)

        DomainModel.delete_domain_relation(cursor, domain_pack_id)

        for domain_name in data['domains']:
            domain_id = None

            sql = "SELECT `id` \
                   FROM `list_domain` \
                   WHERE `domain` = $domain \
                   LIMIT 1"

            replace = dict(domain=domain_name)
            sql = sql_replace(sql, replace)
            cursor.execute(sql)
            db_result = cursor.fetchone()

            if db_result != None:
                domain_id = int(db_result['id'])

            if domain_id == None:
                sql = "INSERT INTO `list_domain` \
                       (`domain`) VALUES ($domain)"

                replace = dict(domain=domain_name)
                sql = sql_replace(sql, replace)
                cursor.execute(sql)
                domain_id = cursor.lastrowid

            sql = "INSERT INTO `rel_domain_pack_domain` \
                   (`domain_pack_id`, `list_domain_id`) \
                   VALUES ($domain_pack_id, $list_domain_id)"

            replace = dict(domain_pack_id=domain_pack_id,
                           list_domain_id=domain_id)

            sql = sql_replace(sql, replace)
            cursor.execute(sql)

        return domain_pack_id

    # -------------- #
    # Update Archive #
    # -------------- #
    @staticmethod
    def update_archive(cursor, id, archived):
        result = None

        sql = "UPDATE `domain_pack` \
               SET `archived` = $archived \
               WHERE `id` = $id"

        replace = dict(id=id, archived=archived)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = int(id)

        return result

    # ------ #
    # Delete #
    # ------ #
    @staticmethod
    def delete(cursor, id):
        DomainModel.delete_domain_relation(cursor, id)

        sql = "DELETE FROM `domain_pack` \
               WHERE `id` = $id"

        replace = dict(id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return True

    # ------------------------- #
    # Delete Targeting Relation #
    # ------------------------- #
    @staticmethod
    def delete_targeting_relation(cursor, targeting_id):
        sql = "DELETE FROM `rel_domain_pack_targeting` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return True

    # -------------------------------- #
    # Delete String Targeting Relation #
    # -------------------------------- #
    @staticmethod
    def delete_string_targeting_relation(cursor, targeting_id):
        sql = "SELECT `list_domain_id` \
               FROM `rel_domain` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        old_list_domain_ids = []

        for db_item in db_result:
            old_list_domain_ids.append(db_item['list_domain_id'])

        sql = "DELETE FROM `rel_domain` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        for old_list_domain_id in old_list_domain_ids:
            DomainModel.delete_if_unused(cursor, old_list_domain_id)

        return True

    # ---------------------- #
    # Delete Domain Relation #
    # ---------------------- #
    @staticmethod
    def delete_domain_relation(cursor, domain_pack_id):
        sql = "SELECT `list_domain_id` \
               FROM `rel_domain_pack_domain` \
               WHERE `domain_pack_id` = $domain_pack_id"

        replace = dict(domain_pack_id=domain_pack_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        old_list_domain_ids = []

        for db_item in db_result:
            old_list_domain_ids.append(db_item['list_domain_id'])

        sql = "DELETE FROM `rel_domain_pack_domain` \
               WHERE `domain_pack_id` = $domain_pack_id"

        replace = dict(domain_pack_id=domain_pack_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        for old_list_domain_id in old_list_domain_ids:
            DomainModel.delete_if_unused(cursor, old_list_domain_id)

        return True

    # --------------------------- #
    # Delete Unused String Domain #
    # --------------------------- #
    @staticmethod
    def delete_if_unused(cursor, list_domain_id):
        sql = "SELECT `id` \
               FROM `rel_domain_pack_domain` \
               WHERE `list_domain_id` = $list_domain_id \
               LIMIT 1"

        replace = dict(list_domain_id=list_domain_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result_1 = cursor.fetchall()

        sql = "SELECT `id` \
               FROM `rel_domain` \
               WHERE `list_domain_id` = $list_domain_id \
               LIMIT 1"

        replace = dict(list_domain_id=list_domain_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result_2 = cursor.fetchall()

        if len(db_result_1) == 0 and len(db_result_2) == 0:
            sql = "DELETE FROM `list_domain` \
                   WHERE `id` = $list_domain_id"

            replace = dict(list_domain_id=list_domain_id)
            sql = sql_replace(sql, replace)
            cursor.execute(sql)