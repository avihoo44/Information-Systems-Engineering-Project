# ------------------------------------------------------
# db_handler.py
# ------------------------------------------------------
# communication between python and mysql database
# ------------------------------------------------------
# Last updated - 2019-01-12                                
# ------------------------------------------------------
# Created by: Tal Eylon, Avihoo Menahem, Amihai Kalev
# ------------------------------------------------------

# import the required libraries & code
import logging
import os
#import DB library IMPORTANT
import MySQLdb

# Database connection parameters 
DB_USER_NAME='project05'
DB_PASSWORD='vcaqqywp'
DB_DEFALUT_DB='project05'

###########################
## This class handles the database communication.
## Initialized by: user name, password, host, port, socket (to differ google app engine environment with appspot.com environment)
## plus an empty connection object.
###########################
class DbHandler():
	def __init__(self):
		logging.info('Initializing a new DbHandler')
		self.m_user=DB_USER_NAME
		self.m_password=DB_PASSWORD
		self.m_default_db=DB_DEFALUT_DB
		self.m_unixSocket='/cloudsql/dbcourse2015:mysql'
		self.m_charset='utf8'
		self.m_host='173.194.228.96'
		self.m_port=3306
		self.m_DbConnection=None

	def connectDb(self): #Connect to the database
		logging.info('In ConnectToDb')
		# Make sure we will connect to the DB only once:
		if self.m_DbConnection is None:
			env = os.getenv('SERVER_SOFTWARE') #we are at appspot.com environment
			if (env and env.startswith('Google App Engine/')):
				#Running from Google App Engine
				logging.info('In env - Google App Engine')
				# connect to the DB
				self.m_DbConnection = MySQLdb.connect(
				unix_socket=self.m_unixSocket,
				user=self.m_user,
				passwd=self.m_password,
				charset=self.m_charset,
				db=self.m_default_db)
			else:
				#Connecting from an external network.
				logging.info('In env - Launcher') #we are at google app engine environment
				# connect to the DB
				self.m_DbConnection = MySQLdb.connect(
				host=self.m_host,
				db=self.m_default_db,
				port=self.m_port,
				user= self.m_user,
				passwd=self.m_password,
				charset=self.m_charset)
			logging.info('Connected Successfully!') 

	def disconnectDb(self): #disconnect from database
		logging.info('In DisconnectFromDb')
		if self.m_DbConnection:
			self.m_DbConnection.close()
		logging.info('Disconnected successfully!')
			
	def commit(self): #apply database changes such as DDL, DML and DQL queries
		logging.info('In commit')
		if self.m_DbConnection:
			self.m_DbConnection.commit()			
			
	def getCursor(self): #handle database queries, essential to database communication
		logging.info('In DbHandler.getCursor')
		self.connectDb()
		return (self.m_DbConnection.cursor())
	
	def status(self): #returns TRUE if connected to DB
		if self.m_DbConnection is None:
			return False
		else:
			return True
				


									  