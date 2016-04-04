from functions import *
from mtime import *


###################
### Time Matrix ###
###################
class TimeMatrixModel(object):
    # ------------------------ #
    # Get List By Targeting Id #
    # ------------------------ #
    @staticmethod
    def get_targeting_list(cursor, targeting_id):
        sql = "SELECT \
               `tm`.`list_day_id` AS `tm.list_day_id`, \
               `tm`.`list_start_time_id` AS `tm.list_start_time_id`, \
               `tm`.`list_end_time_id` AS `tm.list_end_time_id`, \
               `d`.`day` AS `d.day` \
               FROM `rel_timematrix` AS `tm` \
               INNER JOIN `list_day` AS `d` \
               ON `tm`.`list_day_id` = `d`.`id` \
               WHERE `tm`.`targeting_id` = $targeting_id"

        replace = dict(targeting_id=str(targeting_id))
        sql = sql_replace(sql, replace)
        cursor.execute(sql)        
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            start_id = db_item['tm.list_start_time_id']
            end_id = db_item['tm.list_end_time_id']
            start = {'id': start_id, 'time': str(TimeModel.get(cursor, start_id))}
            end = {'id': end_id, 'time': str(TimeModel.get(cursor, end_id))}

            result.append({
                'day': {
                    'id': db_item['tm.list_day_id'],
                    'name': db_item['d.day']
                },
                'start': start,
                'end': end
            })
 
        return result

    # ------------------------ #
    # Get Ids By Targeting Id #
    # ------------------------ #
    @staticmethod
    def get_targeting_ids_list(cursor, targeting_id):
        sql = "SELECT \
               `list_day_id`, \
               `list_start_time_id`, \
               `list_end_time_id` \
               FROM `rel_timematrix` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=str(targeting_id))
        sql = sql_replace(sql, replace)
        cursor.execute(sql)        
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            result.append({
                'dayId': db_item['list_day_id'],
                'startTimeId': db_item['list_start_time_id'],
                'endTimeId': db_item['list_end_time_id']
            })
 
        return result

    # ------------------------------ #
    # Get Related With Targeting Ids #
    # ------------------------------ #
    @staticmethod
    def get_targeting_relation(cursor, targeting_id):
        sql = "SELECT \
               `list_day_id` AS `d`, \
               `list_start_time_id` AS `s`, \
               `list_end_time_id` AS `e` \
               FROM `rel_timematrix` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=str(targeting_id))
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        db_result = cursor.fetchall()
        result = []

        for db_item in db_result:
            d = str(db_item['d'])
            s = str(db_item['s'])
            e = str(db_item['e'])
            result.append(d + '|' + s + '|' + e)

        result.sort()

        if result == None:
            result = []

        return result

    # ------------------------- #
    # Create Targeting Relation #
    # ------------------------- #
    @staticmethod
    def create_targeting_relation(cursor, day_id, start_id, end_id, targeting_id):
        sql = "INSERT INTO `rel_timematrix` ( \
               `list_day_id`, \
               `list_start_time_id`, \
               `list_end_time_id`, \
               `targeting_id` \
               ) VALUES ( \
               $day_id, \
               $start_id, \
               $end_id, \
               $targeting_id \
               )"

        replace = dict(day_id=str(day_id),
                       start_id=str(start_id),
                       end_id=str(end_id),
                       targeting_id=str(targeting_id))

        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return True

    # ------------------------- #
    # Delete Targeting Relation #
    # ------------------------- #
    @staticmethod
    def delete_targeting_relation(cursor, targeting_id):
        sql = "DELETE FROM `rel_timematrix` \
               WHERE `targeting_id` = $targeting_id"

        replace = dict(targeting_id=str(targeting_id))
        sql = sql_replace(sql, replace)
        cursor.execute(sql)

        return True