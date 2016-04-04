from ..functions import *


###########
### OSS ###
###########
class OSSModel(object):
    # ------------- #
    # Get Full List #
    # ------------- #
    @staticmethod
    def get_list(cursor):
        sql = "SELECT \
               `id` AS `id`, \
               `oss` AS `value` \
               FROM `list_oss`"

        cursor.execute(sql)

        return cursor.fetchall()

    # ------------------ #
    # Get List By Search #
    # ------------------ #
    @staticmethod
    def get_search_list(cursor, search):
        sql = "SELECT \
               `id` AS `id`, \
               `oss` AS `value` \
               FROM `list_oss` \
               WHERE `oss` LIKE $search"

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
               `list`.`oss` AS `value` \
               FROM `rel_oss` AS `rel` \
               INNER JOIN `list_oss` AS `list` \
               ON `rel`.`list_oss_id` = `list`.`id` \
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
        sql = "SELECT `list_oss_id` \
               FROM `rel_oss` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            result.append(int(db_item['list_oss_id']))

        result.sort()

        if result == None:
            result = []

        return result

    # ------------------------- #
    # Create Targeting Relation #
    # ------------------------- #
    @staticmethod
    def create_targeting_relation(cursor, id, targeting_id):
        sql = "INSERT INTO `rel_oss` \
               (`list_oss_id`, `targeting_id`) \
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
        sql = "DELETE FROM `rel_oss` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=targeting_id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return True