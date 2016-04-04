from flaskext.mysql import MySQLdb
from settings import *


class DB(object):
	cursor = None
	connection = None

	@staticmethod
	def mysql_config(app, mysql):
		app.config['MYSQL_DATABASE_USER'] = DATABASE_USER
		app.config['MYSQL_DATABASE_PASSWORD'] = DATABASE_PASSWORD
		app.config['MYSQL_DATABASE_DB'] = DATABASE_DB
		app.config['MYSQL_DATABASE_HOST'] = DATABASE_HOST
		mysql.init_app(app)

	@staticmethod
	def mysql_connect(mysql):
		DB.connection = mysql.connect()
		DB.cursor = DB.connection.cursor(MySQLdb.cursors.DictCursor)