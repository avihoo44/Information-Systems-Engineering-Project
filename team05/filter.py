# ------------------------------------------------------
# filter.py
# ------------------------------------------------------
# handles the ability to filter the dog walkers for the dog owner
# ------------------------------------------------------
# Last updated - 2019-01-12                                
# ------------------------------------------------------
# Created by: Tal Eylon, Avihoo Menahem, Amihai Kalev
# ------------------------------------------------------

# import the required libraries & code
import db_handler
import logging

###########################
## This class handles the filter process.
## Initialized by: email, type_id, row_count=0, an empy dictionary named data
## Each filter will inherit from this main filter class.
###########################
class Filter:
	def __init__(self, email, type_id):
		self.email = email
		self.type_id = type_id
		self.data = {}
		self.row_count = 0
	
	def calculateAvailable(self): ##Calculate available dogwalkers
		count = 0
		for each_dogwalker in self.data:
			if each_dogwalker[5] != each_dogwalker[7]: #if dogwalkers limit did not cross
				count += 1
		logging.info("Available Dogwalkers found: "+str(count))
		return count
	
	def getRowCount(self): ## get rows count --> number of dogwalkers
		return self.row_count

###########################
## This class handles the filter by day process.
## Initialized by: Filter __init__, relevant day
###########################
class ByDay(Filter):
	def __init__(self, email, day, type_id):
		Filter.__init__(self,email,type_id)
		self.day = day
		logging.info("Assigned filter:\n Day: "+str(self.day)+", Type_ID: "+str(self.type_id))
	
	def getByDay(self): #apply fliter
		try:
			#### DATABASE CONNECTION ####
			db_connection = db_handler.DbHandler()
			db_connection.connectDb()
			#### DEFINE CURSOR OBJECT ####
			cursor = db_connection.getCursor()
			#### SQL QUERY AND EXECUTE: ####

			sql_query = """ SELECT Person.p_name, Person.email, Person.city, swd.Day_Of_Work, dw.Day_Price, dw.Max_DogsPerDay, takeo.Type_ID, COUNT(td.dog_id)
							FROM ((Specific_Working_Days as swd LEFT JOIN Taking_Dogs td on swd.email=td.email and swd.day_of_work=td.day_of_work) join Dog_Walker as dw on dw.email=swd.email) join Person on Person.email=dw.email
							join Takes_Only as takeo ON dw.email = takeo.email
							WHERE swd.day_of_work=%s AND Type_ID = %s
							GROUP BY Person.p_name, Person.email, Person.city, swd.Day_Of_Work, dw.Day_Price, dw.Max_DogsPerDay, takeo.Type_ID """
			self.row_count = cursor.execute(sql_query, (self.day,self.type_id,))
			self.data = cursor.fetchall()
			logging.info("filter: "+str(self.data))
		except Exception as e: #in case of an error, catch it and print it to the log
			logging.info("Error: "+str(e))
			return False
		finally: #### IMPORTANT ####
			if db_connection.status(): # Make sure to disconnect from DB no matter what
				db_connection.disconnectDb() ##DISCONNECT##
		
		return self.data
		
###########################
## This class handles the filter by city process.
## Initialized by: Filter __init__, relevant city
###########################
class ByCity(Filter):
	def __init__(self, email, city, type_id):
		Filter.__init__(self,email,type_id)
		self.city = city
		logging.info("Assigned filter:\n City: "+self.city+", Type_ID: "+str(self.type_id))
	
	def getByCity(self): #apply fliter
		try:
			#### DATABASE CONNECTION ####
			db_connection = db_handler.DbHandler()
			db_connection.connectDb()
			#### DEFINE CURSOR OBJECT ####
			cursor = db_connection.getCursor()
			#### SQL QUERY AND EXECUTE: ####

			sql_query = """ SELECT Person.p_name, Person.email, Person.city, swd.Day_Of_Work, dw.Day_Price, dw.Max_DogsPerDay, takeo.Type_ID, COUNT(td.dog_id)
							FROM ((Specific_Working_Days as swd LEFT JOIN Taking_Dogs td on swd.email=td.email and swd.day_of_work=td.day_of_work) join Dog_Walker as dw on dw.email=swd.email) join Person on Person.email=dw.email
							join Takes_Only as takeo ON dw.email = takeo.email
							WHERE Person.city=%s AND Type_ID = %s
							GROUP BY Person.p_name, Person.email, Person.city, swd.Day_Of_Work, dw.Day_Price, dw.Max_DogsPerDay, takeo.Type_ID """
			self.row_count = cursor.execute(sql_query, (self.city,self.type_id,))
			self.data = cursor.fetchall()
			logging.info("filter: "+str(self.data))
		except Exception as e: #in case of an error, catch it and print it to the log
			logging.info("Error: "+str(e))
			return False
		finally: #### IMPORTANT ####
			if db_connection.status(): # Make sure to disconnect from DB no matter what
				db_connection.disconnectDb() ##DISCONNECT##
		
		return self.data

		
###########################
## This class handles the filter by max price process.
## Initialized by: Filter __init__, relevant max price
###########################
class ByMaxPrice(Filter):
	def __init__(self, email, max_price, type_id):
		Filter.__init__(self,email,type_id)
		self.max_price = max_price
		logging.info("Assigned filter:\n Max Price: "+str(self.max_price)+", Type_ID: "+str(self.type_id))
	
	def getByMaxPrice(self): # apply filter
		try:
			#### DATABASE CONNECTION ####
			db_connection = db_handler.DbHandler()
			db_connection.connectDb()
			#### DEFINE CURSOR OBJECT ####
			cursor = db_connection.getCursor()
			#### SQL QUERY AND EXECUTE: ####

			sql_query = """ SELECT Person.p_name, Person.email, Person.city, swd.Day_Of_Work, dw.Day_Price, dw.Max_DogsPerDay, takeo.Type_ID, COUNT(td.dog_id)
							FROM ((Specific_Working_Days as swd LEFT JOIN Taking_Dogs td on swd.email=td.email and swd.day_of_work=td.day_of_work) join Dog_Walker as dw on dw.email=swd.email) join Person on Person.email=dw.email
							join Takes_Only as takeo ON dw.email = takeo.email
							WHERE dw.Day_Price<%s AND Type_ID = %s
							GROUP BY Person.p_name, Person.email, Person.city, swd.Day_Of_Work, dw.Day_Price, dw.Max_DogsPerDay, takeo.Type_ID """
						
			self.row_count = cursor.execute(sql_query, (self.max_price,self.type_id,))
			self.data = cursor.fetchall()
			logging.info("filter: "+str(self.data))
		except Exception as e: #in case of an error, catch it and print it to the log
			logging.info("Error: "+str(e))
			return False
		finally: #### IMPORTANT ####
			if db_connection.status(): # Make sure to disconnect from DB no matter what
				db_connection.disconnectDb() ##DISCONNECT##
		
		return self.data
		