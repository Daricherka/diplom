from ..functions import *


###########
### Geo ###
###########
class GeoModel(object):
    # ------------- #
    # Get Full List #
    # ------------- #
    @staticmethod
    def get_list(cursor):
        sql = "SELECT \
               `id` AS `id`, \
               `geo` AS `shortValue`,  \
               `description` AS `value` \
               FROM `list_geo`"

        cursor.execute(sql)

        return cursor.fetchall()

    # ------------------ #
    # Get List By Search #
    # ------------------ #
    @staticmethod
    def get_search_list(cursor, search):
        sql = "SELECT \
               `id` AS `id`, \
               `geo` AS `shortValue`,  \
               `description` AS `value` \
               FROM `list_geo` \
               WHERE `description` LIKE $search"

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
               `list`.`geo` AS `shortValue`,  \
               `list`.`description` AS `value` \
               FROM `rel_geo` AS `rel` \
               INNER JOIN `list_geo` AS `list` \
               ON `rel`.`list_geo_id` = `list`.`id` \
               WHERE `rel`.`targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return cursor.fetchall()

    # ------------------------------ #
    # Get Related With Targeting Ids #
    # ------------------------------ #
    @staticmethod
    def get_targeting_relation(cursor, targeting_id):
        sql = "SELECT `list_geo_id` \
               FROM `rel_geo` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            result.append(int(db_item['list_geo_id']))

        result.sort()

        if result == None:
            result = []

        return result

    # ------------------------- #
    # Create Targeting Relation #
    # ------------------------- #
    @staticmethod
    def create_targeting_relation(cursor, id, targeting_id):
        sql = "INSERT INTO `rel_geo` \
               (`list_geo_id`, `targeting_id`) \
               VALUES ($id, $targeting_id)"

        replace = dict(id=id, targeting_id=targeting_id)

        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return True

    # ------------------------- #
    # Delete Targeting Relation #
    # ------------------------- #
    @staticmethod
    def delete_targeting_relation(cursor, targeting_id):
        sql = "DELETE FROM `rel_geo` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return True