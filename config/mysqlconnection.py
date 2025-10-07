import pymysql.cursors

class MySQLConnection:
	def __init__(self, db):
		connection = pymysql.connect(
			host='localhost',
			user='root',
			password='slayerva666',
			db=db,
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor,
			autocommit=True
		)
		self.connection = connection

	def query_db(self, query, data=None):
		with self.connection.cursor() as cursor:
			cursor.execute(query, data)
			if query.lower().strip().startswith('select'):
				result = cursor.fetchall()
				return result
			else:
				self.connection.commit()
				return cursor.lastrowid

def connectToMySQL(db):
	return MySQLConnection(db)
