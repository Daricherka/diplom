from string import Template
from flaskext.mysql import MySQLdb


def sql_replace(sql, replace):
    sql = ' '.join(sql.split())

    for index in replace:
        if replace[index] == None:
            replace[index] = "NULL"
        else:
            replace[index] = "'" + MySQLdb.escape_string(str(replace[index])) + "'"
    
    return Template(sql).substitute(replace)