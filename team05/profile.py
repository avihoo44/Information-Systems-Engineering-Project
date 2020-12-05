# ------------------------------------------------------
# profile.py
# ------------------------------------------------------
# handles the profile functionality for each dog walker or dog owner
# ------------------------------------------------------
# Last updated - 2019-01-12                                
# ------------------------------------------------------
# Created by: Tal Eylon, Avihoo Menahem, Amihai Kalev
# ------------------------------------------------------

# import the required libraries & code

import db_handler
import logging


###########################
## This global function receives: email, owner_type
## The function will return all relevant data for
## the main profile page of the dog owner.
###########################
def owner_main_page(email, owner_type):
	data = {}
	try:
		#### DATABASE CONNECTION ####
		db_connection = db_handler.DbHandler()
		db_connection.connectDb()
		#### DEFINE CURSOR OBJECT ####
		cursor = db_connection.getCursor()
		
		#### STEP 1: FIND DOG OWNER'S NAME ####
		sql = """ SELECT p_name FROM Person WHERE email = %s """
		cursor.execute(sql, (email,))
		data['dog_owner_name'] = cursor.fetchone()[0] ## Dog Owner's Name
		
		#### STEP 2: FIND DOG OWNER'S TOTAL NUMBER OF DOGS ####
		sql = """ SELECT COUNT(Dog_ID) FROM Has_Dogs WHERE email = %s """
		cursor.execute(sql, (email,))
		data['total_number_of_dogs'] = cursor.fetchone()[0] ## Total number of dogs that belong to the dog owner
		
		#### STEP 3: GET DOG OWNER'S ACCOUNT TYPE ####
		if owner_type == 1:
			data['dog_owner_type'] = "Regular"
		else:
			data['dog_owner_type'] = "Premium"
			
		#### STEP 4: GET DOG OWNER'S LIST OF DOGS ####
		sql = """ SELECT Dog_Name, Dog_Gender, Dog_Age, s.Dog_Type
				  FROM Has_Dogs as hd JOIN Dogs as d ON hd.Dog_ID = d.Dog_ID
									  JOIN Species as s ON d.Type_ID = s.Type_ID
				  WHERE hd.email = %s 
				  GROUP BY Dog_Name, Dog_Gender, Dog_Age, s.Dog_Type """
		row_count = cursor.execute(sql, (email,))
		data['dogs'] = cursor.fetchall()
		data['num_of_dogs'] = row_count #catch the number of rows received in query --> number of dogs that the owner has
	except Exception as e: #in case of an error, catch it and print it to the log
		logging.info("Error: "+str(e))
		return False
	finally: #### IMPORTANT ####
		if db_connection.status(): # Make sure to disconnect from DB no matter what
			db_connection.disconnectDb() ##DISCONNECT##
	
	return data

###########################
## This global function receives: email
## The function will return all relevant data for
## the main profile page of the dog walker.
###########################
def walker_main_page(email):
	data = {}
	try:
		#### DATABASE CONNECTION ####
		db_connection = db_handler.DbHandler()
		db_connection.connectDb()
		#### DEFINE CURSOR OBJECT ####
		cursor = db_connection.getCursor()
		
		#### STEP 1: FIND DOG WALKER'S NAME ####
		sql = """ SELECT p_name FROM Person WHERE email = %s """
		cursor.execute(sql, (email,))
		data['dog_walker_name'] = cursor.fetchone()[0] ## Dog Walker's Name
		
		#### STEP 2: FIND DOG OWNER'S TOTAL WEEK REVENUE ####
		sql = """   SELECT SUM(dw.day_price) 
					FROM Taking_Dogs as td LEFT JOIN Dog_Walker as dw ON dw.email = td.email
					WHERE td.email = %s """
		cursor.execute(sql, (email,))
		data['total_week_revenue'] = cursor.fetchone()[0] ## Total number of dogs that belong to the dog owner
		
		#### STEP 3: GET THE SPECIES THE DOGWALKER IS WILLING TO TAKE ####
		sql = """ SELECT Dog_Type 
				  FROM Takes_Only as tk JOIN Species as s ON tk.type_id = s.type_id
				  WHERE tk.email = %s """
		cursor.execute(sql, (email,))
		data['takes_only'] = cursor.fetchall()
		
		#### STEP 4: GET THE DAYS THE DOGWALKER IS WILLING TO WORK IN ####
		sql = """ SELECT Day_Of_Work FROM Specific_Working_Days
					WHERE email = %s """
		cursor.execute(sql, (email,))
		data['specific_working_days'] = cursor.fetchall()
		logging.info("Specific Working Days: "+str(data))
		
		#### STEP 5: GET DOG WALKER'S CUSTOMERS LIST DISTINCTLY, ORDERED BY THE PERSON'S NAME ####
		sql = """ SELECT re1.Dog_Owner_Name, re1.Dog_Owner_Email, re1.Dog_Owner_Phone_Number, re1.Dog_Owner_City
					FROM Person as p RIGHT JOIN (SELECT td.Email as Email_Walker, p.P_Name as Dog_Owner_Name, dow.Email as Dog_Owner_Email,
														dow.Registration_Date as Dog_Owner_Registration_Date, p.Phone_number as Dog_Owner_Phone_Number,
														p.City as Dog_Owner_City, d.Dog_Name as DogName, td.Day_Of_Work as DayOfWork,
                                                        dw.Day_Price as Revenue
												 FROM Taking_Dogs as td 
                                                 JOIN Has_Dogs as hd on hd.Dog_ID=td.Dog_ID
												 JOIN Dog_Owner as dow on dow.Email=hd.Email
												 JOIN Person as p on dow.Email=p.Email
                                                 JOIN Dogs as d ON hd.Dog_ID = d.Dog_ID
                                                 JOIN Dog_Walker as dw ON td.email = dw.email) AS re1 ON p.Email=re1.Email_walker	
					WHERE p.email=%s
					GROUP BY re1.Dog_Owner_Name, re1.Dog_Owner_Email, re1.Dog_Owner_Phone_Number, re1.Dog_Owner_City 
					ORDER BY re1.Dog_Owner_Name"""
		row_count = cursor.execute(sql, (email,)) #catch the number of rows received in query --> number of customers
		data['customers'] = cursor.fetchall()
		data['customers_num'] = row_count
		
		#### ADD THE LIST OF DAYS ####
		data['days'] = days
		
	except Exception as e: #in case of an error, catch it and print it to the log
		logging.info("Error: "+str(e))
		return False
	finally: #### IMPORTANT ####
		if db_connection.status(): # Make sure to disconnect from DB no matter what
			db_connection.disconnectDb() ##DISCONNECT##
	
	return data

	
###########################
## This global function receives: email
## The function will return all relevant data for
## the schedule presentation of a dog walker.
###########################
def walker_schedule(email):
	data = {}
	try:
		#### DATABASE CONNECTION ####
		db_connection = db_handler.DbHandler()
		db_connection.connectDb()
		#### DEFINE CURSOR OBJECT ####
		cursor = db_connection.getCursor()
			
		### STEP 1: GET DOG WALKER'S SCHEDULE ####
		# receive the list of dog owners that the dog walker scheduled to take for each day of the week.
		
		data = {'day_count': []}
		total_dogs_to_take = 0
		work_schedule = {}
		for each_day in range(1,8): #from sunday to saturday (excluding num 8)
			sql = """ SELECT re1.dog_name, Person.City, Person.p_name, Person.phone_number, Price
						FROM (SELECT Taking_Dogs.Email AS Dog_walker_email, Dogs.Dog_ID,Dogs.Dog_Name, Species.Dog_Type, Taking_Dogs.Day_of_Work, dw.Day_Price as Price
							  FROM Taking_Dogs JOIN Dogs ON Taking_Dogs.Dog_ID=Dogs.dog_ID
											   JOIN Species ON Dogs.type_id=Species.type_id
											   JOIN Dog_Walker as dw ON Taking_Dogs.email = dw.email) as re1
							  JOIN Has_Dogs ON re1.dog_id=Has_Dogs.Dog_ID
							  JOIN Person ON Has_Dogs.Email= Person.Email
						WHERE re1.dog_walker_email=%s AND re1.day_of_work=%s """
			row_count = cursor.execute(sql, (email,each_day,))
			list_of_dogs_to_take = cursor.fetchall()
			work_schedule[each_day] = list_of_dogs_to_take
			total_dogs_to_take += int(row_count)
			data['day_count'].append(row_count)
		
		#### STEP 2: FIND DOG OWNER'S TOTAL WEEK REVENUE ####
		sql = """   SELECT SUM(dw.day_price) 
					FROM Taking_Dogs as td LEFT JOIN Dog_Walker as dw ON dw.email = td.email
					WHERE td.email = %s """
		cursor.execute(sql, (email,))
		data['total_revenue'] = cursor.fetchone()[0]
		
		#### STEP 3: FIND MAX DOGS PER DAY ####
		sql = """ SELECT Max_DogsPerDay FROM Dog_Walker WHERE email = %s """
		cursor.execute(sql, (email,))
		data['max_dogsperday'] = cursor.fetchone()[0]
		data['work_schedule'] = work_schedule # assign work schedule to the data dict
		data['days'] = days # assign the list of days to the data dict
		data['total_dogs_to_take'] = total_dogs_to_take
	except Exception as e: #in case of an error, catch it and print it to the log
		logging.info("Error: "+str(e))
		return False
	finally: #### IMPORTANT ####
		if db_connection.status(): # Make sure to disconnect from DB no matter what
			db_connection.disconnectDb() ##DISCONNECT##
	
	return data

###########################
## This global function returns the species from the database.
###########################	
def show_species():
	try:
		#### DATABASE CONNECTION ####
		db_connection = db_handler.DbHandler()
		db_connection.connectDb()
		#### DEFINE CURSOR OBJECT ####
		cursor = db_connection.getCursor()
		#### GET LIST OF SPECIES ####
		sql = """ SELECT * FROM Species """
		cursor.execute(sql)
		data = cursor.fetchall()
		logging.info(str(data))
	except Exception as e: #in case of an error, catch it and print it to the log
		logging.info("Error: "+str(e))
		return False
	finally: #### IMPORTANT ####
		if db_connection.status(): # Make sure to disconnect from DB no matter what
			db_connection.disconnectDb() ##DISCONNECT##
	
	return data

###########################
## This class handles the new dog addition.
## Initialized by: a list of Dog Name, Dog Gender, Dog Age and Type ID
## along with the dog owner's email.
###########################		
class NewDog:
	def __init__(self, lst, email):
		self.dog_name = lst[0]
		self.dog_gender = lst[1]
		self.dog_age = lst[2]
		self.type_id = lst[3]
		self.email = email
	
	#### this function handles the addition process.
	def add(self):
		try:
			#### DATABASE CONNECTION ####
			db_connection = db_handler.DbHandler()
			db_connection.connectDb()
			#### DEFINE CURSOR OBJECT ####
			cursor = db_connection.getCursor()
			#### SQL QUERY AND EXECUTE: ####
			logging.info("Dog Info: "+self.dog_name+","+self.dog_gender+","+self.dog_age+","+self.type_id) # send to the log the new dog details
			### STEP 1: first insert: dogs table ###
			sql = """ INSERT INTO Dogs(Dog_Name, Dog_Gender, Dog_Age, Type_ID) VALUES (%s,%s,%s,%s) """
			cursor.execute(sql,(self.dog_name,self.dog_gender,self.dog_age,self.type_id,))
			#### COMMIT ####
			db_connection.commit() ## ADD THE DOG
			
			### STEP 2: RETRIEVE THE NEW DOG ID ###
			sql = """ SELECT Max(Dog_ID) FROM Dogs """
			cursor.execute(sql)
			dog_id = cursor.fetchone()
			
			logging.info("new dog_id: "+str(dog_id))
			### STEP 3: second insert: Has Dogs table ###
			sql = """ INSERT INTO Has_Dogs VALUES (%s,%s) """
			cursor.execute(sql,(self.email,dog_id,))
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
## This global function receives: email
## The function will return all relevant data for
## the presentation of all unregistered dogs to a dog walker
## that the dog owner have.
###########################
def getUnregisteredDogs(email):
	try:
		#### DATABASE CONNECTION ####
		db_connection = db_handler.DbHandler()
		db_connection.connectDb()
		#### DEFINE CURSOR OBJECT ####
		cursor = db_connection.getCursor()
		#### GET LIST OF ALL UNREGISTERED DOGS ####
		sql = """ SELECT Dogs.Dog_Name, hd.Dog_ID, Dogs.Type_ID
				  FROM Has_Dogs as hd LEFT JOIN Dogs ON hd.Dog_ID = Dogs.Dog_ID
								LEFT JOIN Taking_Dogs as td ON Dogs.Dog_ID = td.Dog_ID
				  WHERE hd.email = %s AND NOT EXISTS (SELECT Dog_ID 
														FROM Taking_Dogs as td WHERE td.Dog_ID = hd.Dog_ID)"""
		cursor.execute(sql, (email,))
		data = cursor.fetchall()
		logging.info("Unregistered Dogs: "+str(data))
	except Exception as e: #in case of an error, catch it and print it to the log
		logging.info("Error: "+str(e))
		return False
	finally: #### IMPORTANT ####
		if db_connection.status(): # Make sure to disconnect from DB no matter what
			db_connection.disconnectDb() ##DISCONNECT##
	
	return data

def getCities(): #Retrieve currently available dog walkers' cities from the database
	try:
		#### DATABASE CONNECTION ####
		db_connection = db_handler.DbHandler()
		db_connection.connectDb()
		#### DEFINE CURSOR OBJECT ####
		cursor = db_connection.getCursor()
		#### GET LIST OF ALL DOGWALKERS ####
		sql = """ SELECT DISTINCT city FROM Person """
		cursor.execute(sql)
		data = cursor.fetchall() #return without column's name
	except Exception as e: #in case of an error, catch it and print it to the log
		logging.info("Error: "+str(e))
		return False
	finally: #### IMPORTANT ####
		if db_connection.status(): # Make sure to disconnect from DB no matter what
			db_connection.disconnectDb() ##DISCONNECT##
	
	return data

###########################
## This global function receives: email
## The function will return all relevant data for
## the presentation of all assigned dog walkers
## that the dog owner have.
###########################	
def getRelevantDogWalkers(email): ## ASSIGNED DOGWALKERS FOR DOG OWNER
	try:
		#### DATABASE CONNECTION ####
		db_connection = db_handler.DbHandler()
		db_connection.connectDb()
		#### DEFINE CURSOR OBJECT ####
		cursor = db_connection.getCursor()
		#### STEP 1: GET LIST OF ALL ASSGINED DOGWALKERS ####
		sql = """ SELECT d.dog_name, p.p_name, p.phone_number, td.day_of_work, dw.day_price
					FROM Has_Dogs as hd JOIN Taking_Dogs as td ON hd.dog_id = td.dog_id
										JOIN Dog_Walker as dw ON dw.email = td.email
										JOIN Person as p ON dw.email = p.email
										JOIN Dogs as d ON d.dog_id = hd.dog_id
					WHERE hd.email = %s 
					ORDER BY td.day_of_work """
		row_count = cursor.execute(sql, (email,))
		data = cursor.fetchall()
		
		#### STEP 2: GET THE TOTAL COST THAT THE DOG OWNER NEEDS TO PAY ####
		sql = """ SELECT Sum(dw.Day_Price)
					FROM Has_Dogs as hd JOIN Taking_Dogs as td ON hd.dog_id = td.dog_id
										JOIN Dog_Walker as dw ON dw.email = td.email
										JOIN Person as p ON dw.email = p.email
										JOIN Dogs as d ON d.dog_id = hd.dog_id
					WHERE hd.email = %s """
		cursor.execute(sql, (email,))
		total_cost = cursor.fetchone()[0]
		logging.info("Assigned Dog Walkers: "+str(data)+"\n Total Cost: "+str(total_cost)+"Num of Dog walkers:"+str(row_count))
	except Exception as e: #in case of an error, catch it and print it to the log
		logging.info("Error: "+str(e))
		return False
	finally: #### IMPORTANT ####
		if db_connection.status(): # Make sure to disconnect from DB no matter what
			db_connection.disconnectDb() ##DISCONNECT##
	
	return [data,total_cost,row_count]
	
### MAIN DAYS LIST ###
days = ["Sunday", "Monday", "Tuesday", "Wednseday", "Thursday", "Friday", "Saturday"]