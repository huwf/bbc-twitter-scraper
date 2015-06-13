import sqlite3

database_name = '2014-07-02.db'

class Database:
	dbName = database_name
	def __init__(self, dbName = database_name):
		#print("Database constructor")
		self.databaseName = dbName
		self.conn = sqlite3.connect(self.databaseName)		
		self.conn.row_factory = sqlite3.Row
		self.cur = self.conn.cursor()
		self.dbName = dbName

	def __del__(self):
		print "Committing and closing DB connection\n"
		self.conn.commit()
		self.conn.close()

	def insertQuery(self, query, parameters = ''):
		'''
		Inserts a value into the database. Returns lastrowid
		'''
		self.cur.execute(query, parameters)
		self.conn.commit()
		return self.cur.lastrowid

	def selectQuery(self, query, parameters = ''):
		'''
		Performs a select query, and returns a list of the results
		'''
		self.cur.execute(query, parameters)
		return self.cur.fetchall()

	def selectQueryAsList(self, query, parameters = ''):
		'''
		If I have a list of stuff with only one field, enter the field as colName, and
		then add it to a new list to return
		'''
		listy = []
		for q in self.selectQuery(query, parameters):
			listy.append(q[0])
		return listy

	def singleValueSelectQuery(self, query, parameters = ''):		
		self.cur.execute(query, parameters)
		
		try:
			return self.cur.fetchone()[0]
		except:			
			return None
		
		

	def updateQuery(self, query, parameters = ''):
		self.cur.execute(query, parameters)
		self.conn.commit()
		return self.cur.rowcount