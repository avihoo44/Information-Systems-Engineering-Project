# ------------------------------------------------------
# checks.py
# ------------------------------------------------------
# handles checks, such as recognizing the connected user
# ------------------------------------------------------
# Last updated - 2019-01-12                                
# ------------------------------------------------------
# Created by: Tal Eylon, Avihoo Menahem, Amihai Kalev
# ------------------------------------------------------

# import the required libraries & code
import db_handler
import logging

###########################
## This global function receives: email
## return 0 if person isn't registered in database.
## return 1 if person is a regular dog owner.
## return 2 if person is a premium dog owner.
## return 3 if personis a dog walker.
###########################	
def recognize_person(email):
	try:
		logging.info("Recognizing person")
		#### DATABASE CONNECTION ####
		db_connection = db_handler.DbHandler()
		db_connection.connectDb()
		#### DEFINE CURSOR OBJECT ####
		cursor = db_connection.getCursor()
		#### SQL QUERY AND EXECUTE: ####
		sql_query = """ SELECT email FROM Person WHERE email = %s """
		person_exists = cursor.execute(sql_query, (email,)) #returns 0 if no row has been fetched
		logging.info(str(person_exists)) # log value
		if person_exists == 0:
			logging.info("Person isn't in database")
			return 0 #return 0 if the user is not registered at all
			
		#### SQL QUERY AND EXECUTE: ####
		sql_query = """ SELECT email FROM Dog_Owner WHERE email = %s """
		dog_owner_exists = cursor.execute(sql_query, (email,)) #returns 0 if person isn't a dog owner
		
		sql_query = """ SELECT email FROM Dog_Walker WHERE email = %s """
		dog_walker_exists = cursor.execute(sql_query, (email,)) #returns 0 if person isn't a dog walker
		if dog_owner_exists == 1:
			### Check if dog owner is a regular user:
			sql_query = """ SELECT email FROM Regular_Dog_Owner WHERE email = %s """
			reg_dog_owner = cursor.execute(sql_query, (email,)) #returns 0 if person isn't a regular dog owner
			if reg_dog_owner == 1:
				logging.info("Person was recognized as a Regular Dog Owner")
				return 1
			else:
				logging.info("Person was recognized as a Premium Dog Owner")
				return 2
		
		if dog_walker_exists == 1:
			logging.info("Person was recognized as Dog Walker")
			return 3
			
	except Exception as e: #in case of an error, catch it and print it to the log
		logging.info("Error: "+str(e)) 
		return False
	finally:
		if db_connection.status(): # Make sure to disconnect from DB no matter what
			db_connection.disconnectDb() ##DISCONNECT##

	
	
	