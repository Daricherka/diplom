from functions import *


############
### Time ###
############
class TimeModel(object):
    # --------- #
    # Get By Id #
    # --------- #
    @staticmethod
    def get(cursor, id):
        sql = "SELECT \
               `time` AS `time` \
               FROM `list_time` \
               WHERE `id` = $id"
        
        replace = dict(id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        result = cursor.fetchone()

        if result == None:
            return None

        return result['time']