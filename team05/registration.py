# ------------------------------------------------------
# registration.py
# ------------------------------------------------------
# handles the registration process to the database
# ------------------------------------------------------
# Last updated - 2019-01-12                                
# ------------------------------------------------------
# Created by: Tal Eylon, Avihoo Menahem, Amihai Kalev
# ------------------------------------------------------

# import the required libraries & code
import logging
import db_handler

###########################
## This class handles the regular dog owner registration process.
## Initialized by: A list of Email, Name, Phone, City in order to create a person,
## plus a default monthly comission.
###########################
class RegisterRegDogOwner:
	def __init__(self, lst, monthly_comission=25):
		self.email = lst[0]
		self.name = lst[1]
		self.phone = lst[2]
		self.city = lst[3]
		self.monthly_comission = monthly_comission
	
	def register(self): # apply registration
		try:
			#### DATABASE CONNECTION ####
			db_connection = db_handler.DbHandler()
			db_connection.connectDb()
			#### DEFINE CURSOR OBJECT ####
			cursor = db_connection.getCursor()
			#### SQL QUERY AND EXECUTE: ####
			### STEP 1: first insert: person table ###
			sql = """ INSERT INTO Person VALUES (%s,%s,%s,%s) """
			cursor.execute(sql,(self.email,self.name,self.phone,self.city,))
			
			### STEP 2: second insert: Dog Owner
			sql = """ INSERT INTO Dog_Owner VALUES (%s,CURDATE()) """
			cursor.execute(sql,(self.email,))
			
			## STEP 3: third insert: Regular_Dog_Owner
			sql = """ INSERT INTO Regular_Dog_Owner VALUES (%s,%s) """
			cursor.execute(sql, (self.email,self.monthly_comission,))
			
			## COMMIT ##
			db_connection.commit()
		except Exception as e: #in case of an error, catch it and print it to the log
			logging.info("Error: "+str(e)) 
			return False #return False in case of an error
		finally:
			if db_connection.status(): # Make sure to disconnect from DB no matter what
				db_connection.disconnectDb() ##DISCONNECT##
		
		return True #return True if registration was successfull

###########################
## This class handles the premium dog owner registration process.
## Initialized by: A list of Email, Name, Phone, City in order to create a person,
## A full addres and a default yearly comission.
###########################
class RegisterPremDogOwner:
	def __init__(self, lst):
		self.email = lst[0]
		self.name = lst[1]
		self.phone = lst[2]
		self.city = lst[3]
		self.full_address = lst[4]
		self.yearly_comission = 250 #default yearly comission of 250 shekels.
	
	def register(self): #apply registration
		try:
			db_connection = db_handler.DbHandler()
			### check that the user has entered a full address ###
			if not self.full_address:
				raise ValueError("Incorrect parameters")
			
			#### DATABASE CONNECTION ####
			db_connection.connectDb()
			#### DEFINE CURSOR OBJECT ####
			cursor = db_connection.getCursor()
			#### SQL QUERY AND EXECUTE: ####
			### STEP 1: first insert: person table ###
			sql = """ INSERT INTO Person VALUES (%s,%s,%s,%s) """
			cursor.execute(sql,(self.email,self.name,self.phone,self.city,))
			
			### STEP 2: second insert: Dog Owner
			sql = """ INSERT INTO Dog_Owner VALUES (%s,CURDATE()) """
			cursor.execute(sql,(self.email,))
			
			## STEP 3: third insert: Premium_Dog_Owner
			sql = """ INSERT INTO Premium_Dog_Owner VALUES (%s,%s,%s) """
			cursor.execute(sql, (self.email,self.yearly_comission,self.full_address,))
			
			## COMMIT ##
			db_connection.commit()
		except Exception as e: #in case of an error, catch it and print it to the log
			logging.info("Error: "+str(e))
			return False #return False in case of an error
		finally:
			if db_connection.status(): # Make sure to disconnect from DB no matter what
				db_connection.disconnectDb() ##DISCONNECT##
		
		return True #return True if registration was successful

###########################
## This class handles the dog walker registration process.
## Initialized by: A list of Email, Name, Phone, City in order to create a person,
## A day price and a number of maximum dogs per day the dog walker can take.
###########################		
class RegisterDogWalker:
	def __init__(self, lst, takes_only, specific_working_days):
		self.email = lst[0]
		self.name = lst[1]
		self.phone = lst[2]
		self.city = lst[3]
		self.day_price = lst[4]
		self.max_dogsperday = lst[5]
		
		if not takes_only: ## if the user hasn't selected any of the dog species
			self.takes_only = range(1,9) #Apply a list of all dog types
		else:
			self.takes_only = takes_only #Apply a list of the specific dog types the user chose
		
		if not specific_working_days: ## if the user hasn't selected any of the days
			self.specific_working_days = range(1,8) #Apply a list of all working days
		else:
			self.specific_working_days = specific_working_days #Apply a list of the specific working days the user chose
	
	def register(self): #apply registration
		try:
			#### DATABASE CONNECTION OBJECT ####
			db_connection = db_handler.DbHandler()
			### CONNECT TO DB ###
			db_connection.connectDb()
			#### DEFINE CURSOR OBJECT ####
			cursor = db_connection.getCursor()
			#### SQL QUERY AND EXECUTE: ####
			### STEP 1: first insert: person table ###
			sql = """ INSERT INTO Person VALUES (%s,%s,%s,%s) """
			cursor.execute(sql,(self.email,self.name,self.phone,self.city,))
			
			### STEP 2: second insert: Dog Walker table
			sql = """ INSERT INTO Dog_Walker VALUES (%s,%s,%s) """
			cursor.execute(sql,(self.email,self.day_price,self.max_dogsperday,))
			
			## STEP 3: third insert: Specific working days table
			for each_day in self.specific_working_days:
				sql = """ INSERT INTO Specific_Working_Days VALUES (%s,%s) """
				cursor.execute(sql,(self.email,each_day,))
			
			## COMMIT ##
			db_connection.commit()
			
			## STEP 4: forth insert: Takes only table
			for each_dogtype in self.takes_only:
				sql = """ INSERT INTO Takes_Only VALUES (%s,%s) """
				cursor.execute(sql,(self.email,each_dogtype,))
				
			## COMMIT ##
			db_connection.commit()
		except Exception as e: #in case of an error, catch it and print it to the log
			logging.info("Error: "+str(e))
			return False #return False in case of an error
		finally:
			if db_connection.status(): # Make sure to disconnect from DB no matter what
				db_connection.disconnectDb() ##DISCONNECT##
		
		return True #return True if registration was successful

###########################
## This global function receives: data (relevant for dog registration with walker)
## Handles the registration process of a dog to a dog walker.
###########################			
def register_dog(data):
	try:
		logging.info("data contains: "+str(data))
		#### DATABASE CONNECTION ####
		db_connection = db_handler.DbHandler()
		db_connection.connectDb()
		#### DEFINE CURSOR OBJECT ####
		cursor = db_connection.getCursor()
		### SQL QUERY AND EXECUTE: ####
		### INSERT TO TAKING_DOGS ###
		sql = """ INSERT INTO Taking_Dogs VALUES (%s,%s,%s) """
		cursor.execute(sql,(data[0],data[1],data[2],))
		
		## COMMIT ##
		db_connection.commit()
	except Exception as e: #in case of an error, catch it and print it to the log
		logging.info("Error: "+str(e)) 
		return False #return False in case of an error
	finally:
		if db_connection.status(): # Make sure to disconnect from DB no matter what
			db_connection.disconnectDb() ##DISCONNECT##
	
	return True #return True if registration was successful