# ------------------------------------------------------
# DogWalkers Project: Main program
# ------------------------------------------------------
# This program handles the communication between the HTML pages and the python code.
# For each defined url, this program will show, calcualte and get the relevant data.
# ------------------------------------------------------
# Last updated - 2019-01-12                                
# ------------------------------------------------------
# Created by: Tal Eylon, Avihoo Menahem, Amihai Kalev
# ------------------------------------------------------

# import the required core libraries & code
import webapp2 # communication between handlers and python
import jinja2 # communication between html pages and python
import os # operating system library
import db_handler # communication between python and mysql database
import logging # communication between python and google app engine logging
from google.appengine.api import users # communication between python and google users

# import the relevant project python files
import checks # handles checks, such as recognizing the connected user
import registration # handles the registration process to the database
import profile # handles the profile functionality for each dog walker or dog owner
import filter as filters # handles the ability to filter the dog walkers for the dog owner

###### login_required DECORATOR #####
# define the ability to force login in case the user
# who visits a web page isn't connected.

def login_required(handler_method):
    """A decorator to require that a user be logged in to access a handler.
		We will redirect to a login page if the user is not logged in
    """
    def check_login(self, *args, **kwargs):
        user = users.get_current_user()
        if not user:
            return self.redirect(users.create_login_url(self.request.url))
        else:
            handler_method(self, *args, **kwargs)

    return check_login
	

###### Set the Jinja2 Environment ######
jinja_environment = jinja2.Environment(	loader=
										jinja2.FileSystemLoader(os.path.dirname(__file__)))


############################################################
########################  HANDLERS  ########################
############################################################										
										
# -------------------------------------------------------------
# This class will handle the main page.
# The user here will be requested to sign in.
# Handles: '/'
# -------------------------------------------------------------
class MainPage(webapp2.RequestHandler):
	# When we receive an HTTP GET request - display the main page.
	def get(self):
		# Display main_page.html page using jinja
		template = jinja_environment.get_template('main_page.html')
		self.response.write(template.render())


# -------------------
# This class allows the user to log out.
# Handles '/logout'
# ------------------------					
class Logout(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user() # get current user connection status
		if not user:
			self.redirect('/') # redirect to main page if he is already logged out
		else:
	 	   self.redirect(users.create_logout_url(dest_url='/')) # log the user out and redirect to main page

		   
# -------------------
# This class allows the user to log in.
# If he's not regsitered in the database, redirect to registration.
# Else, redirect to the relevant profile page.
# Handles '/login'
# ------------------------	
class Login(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user() # get current user connection status
		if not user:
			return self.redirect(users.create_login_url(dest_url='/login'))
		
		result = checks.recognize_person(user.email())
		#################################################################
		### if result is 0, then the person isn't registered in database.
		### if result is 1, then the person is a regular dog owner.
		### if result is 2, then the person is a premium dog owner.
		### if result is 3, then the person is a dog walker.
		#################################################################
		if result == 0: 
			template = jinja_environment.get_template('choose_register.html') #show the registeration selection page
			return self.response.write(template.render())
		elif result == 1 or result == 2:
			self.redirect('/owner/profile')
		elif result == 3:
			self.redirect('/walker/profile')

			
# -------------------
# This class allows the user to register as a dog owner.
# The class differentiates between a regular and a premium dog owner.
# His details will be entered to the database.
# Handles '/registerdogowner'
# ------------------------	
class DogOwner(webapp2.RequestHandler):
	def post(self):
		#### If the user has just arrived from the registration selection page,
		#### Show him the relevant registration page.
		if not self.request.get('name'):
			template = jinja_environment.get_template('dog_owner_registration.html')
			return self.response.write(template.render())
		
		### Prepare data for registration ###
		lst = []
		user = users.get_current_user()
		lst.append(user.email())
		lst.append(self.request.get('name'))
		lst.append(self.request.get('phone'))
		lst.append(self.request.get('city'))
		
		if self.request.get('dog_owner_account') == "reg": 
			#### REGULAR DOG OWNER REGISTRATION
			#### REGISTER:
			account = registration.RegisterRegDogOwner(lst)
			logging.info("parameters: "+str(lst))
			result = account.register()
		elif self.request.get('dog_owner_account') == "prem": 
			#### PREMIUM DOG OWNER REGISTRATION
			#### RECEIVE THE FULL ADDRESS OF THE PREMIUM DOG OWNER ####
			lst.append(self.request.get('full_address'))
			#### REGISTER:
			account = registration.RegisterPremDogOwner(lst)
			result = account.register()
		else: # in case an unpredicted error has occurred
			return self.redirect('/') #redirect to main page
	
		#### CHECK REGISTRATION STATUS ####
		template = jinja_environment.get_template('registration_status.html')
		if result: # will be false in case the registration failed
			logging.info("dog owner registration success")
			status = {'data': 1} #registration success
		else:
			logging.info("dog owner registration fail")
			status = {'data': 2} #registration failed
		
		#prepare the relevant response about the registration
		template = jinja_environment.get_template('registration_status.html')
		return self.response.write(template.render(status))
	
	def get(self): #if a user accidentally entered the page, redirect him to main page. 
		return self.redirect('/')

# -------------------
# This class allows the user to register as a dog walker.
# His details will be entered to the database.
# Handles '/registerdogwalker'
# ------------------------			
class DogWalker(webapp2.RequestHandler):
	def post(self):
		#### If the user has just arrived from the registration selection page,
		#### Show him the relevant registration page.
		if not self.request.get('name'):
			template = jinja_environment.get_template('dog_walker_registration.html')
			return self.response.write(template.render())
		
		user = users.get_current_user()
		lst = [] #receive person attributes
		lst.append(user.email())
		lst.append(self.request.get('name'))
		lst.append(self.request.get('phone'))
		lst.append(self.request.get('city'))
		lst.append(self.request.get('day_price'))
		lst.append(self.request.get('max_dogsperday'))
		work_days = self.request.get_all('specific_working_days')
		dog_types = self.request.get_all('dog_types')
		logging.info("Dog Walker registration: retrieved parameters successfully")
		
		#### REGISTER ###			
		account = registration.RegisterDogWalker(lst, dog_types, work_days)
		result = account.register()
		
		#### CHECK REGISTRATION STATUS ####
		if result: # will be false in case the registration failed
			logging.info("dog walker registration success")
			status = {'data': 1} #registration success
		else:
			logging.info("dog walker registration fail")
			status = {'data': 2} #registration failed
		
		#prepare the relevant response about the registration
		template = jinja_environment.get_template('registration_status.html')
		return self.response.write(template.render(status))
	
	def get(self):
		return self.redirect('/')



###############################################################################
##################################           ##################################
################################## DOG OWNER ##################################
##################################           ##################################
###############################################################################

# -------------------
# This class handles the dog owner profile page.
# Handles '/owner/profile'
# ------------------------	
class ProfileDogOwner(webapp2.RequestHandler):
	@login_required
	def get(self):
		user = users.get_current_user() # get current user connection status
		result = checks.recognize_person(user.email())
		if result == 3: # a dog walker entered dog owner zone
			return self.redirect('/walker/profile') #redirect dog walker to his profile page
		elif result == 0:
			return self.redirect('/') #in case the person does not exist in database
		
		data = profile.owner_main_page(user.email(),result) #prepare the data for the dog owner profile
		template = jinja_environment.get_template('profile_dogowner.html')
		self.response.write(template.render(data))
		
# -------------------
# This class handles the request of the dog owner to add a new dog.
# Handles '/owner/profile/add'
# ------------------------	
class AddADog(webapp2.RequestHandler):
	@login_required
	def get(self):
		user = users.get_current_user() # get current user connection status
		result = checks.recognize_person(user.email())
		if result == 3: # a dog walker entered dog owner zone
			return self.redirect('/walker/profile') #redirect dog walker to his profile page
		
		#prepare the relevant web page
		template = jinja_environment.get_template('/add_a_dog.html')
		data = {'species': profile.show_species() }
		self.response.write(template.render(data))
	
	def post(self):
		### The user had sent a form by post method
		lst = []
		user = users.get_current_user()
		lst.append(self.request.get('dog_name'))
		lst.append(self.request.get('dog_gender'))
		lst.append(self.request.get('dog_age'))
		lst.append(self.request.get('type_id'))
		
		#### DEFINE THE NEW DOG AND ADD IT ####
		new_dog = profile.NewDog(lst, user.email())
		result = new_dog.add()
		
		#### CHECK DOG ADDITION STATUS ####
		if result:# will be false in case the registration failed
			logging.info("dog registration was successful")
			status = {'data': 1} #registration success
		else:
			logging.info("dog registration fail")
			status = {'data': 2} #registration failed
		
		#prepare the relevant response about the dog addition
		template = jinja_environment.get_template('add_a_dog_status.html')	
		return self.response.write(template.render(status))
			
# -------------------
# This class handles the dog owner request to register his dog to a dog walker,
# one at a time, by specific criteria.
# Handles '/owner/profile/filter'
# ------------------------	
class ShowByFilter(webapp2.RequestHandler):
	@login_required
	def get(self): #when the dog owner wants to view all his unregistered dogs
		user = users.get_current_user() # get current user connection status
		result = checks.recognize_person(user.email())
		if result == 3: # a dog walker entered dog owner zone
			return self.redirect('/walker/profile') #redirect dog walker to his profile page
		
		### Receive the unregistered dogs along with the available cities
		template = jinja_environment.get_template('filter.html')
		data = {
		'dogs_unregistered': profile.getUnregisteredDogs(user.email()),
		'cities': profile.getCities()
		}
		logging.info(str(data['dogs_unregistered']))
		self.response.write(template.render(data))
	
	def post(self): #when the dog owner wants to filter the view of dog walkers
		user = users.get_current_user()
		### receive the dog id and the dog type
		dog_id_and_type = self.request.get('dog_id_and_type')
		dog_id_and_type = dog_id_and_type.split(",")
		data = {
		'dog_id': dog_id_and_type[0],
		'days': profile.days # a list of the days while 1 is sunday, 2 is monday ... 7 is saturday
		}
		
		### Now, according to the selected filter, show the relevant dog walkers: ###
		if self.request.get('chosen_filter') == "city": 
			############# FILTER BY CITY #############
			city = self.request.get('city')
			filter = filters.ByCity(user.email(),city,dog_id_and_type[1])
			data['dog_walkers']= filter.getByCity()
			
		elif self.request.get('chosen_filter') == "day": 
			############# FILTER BY DAY #############
			day = self.request.get('day')
			filter = filters.ByDay(user.email(),day, dog_id_and_type[1])
			data['dog_walkers']= filter.getByDay()
			
		elif self.request.get('chosen_filter') == "maxprice":
			############# FILTER BY MAX PRICE #############
			max_price = self.request.get('max_price')
			filter = filters.ByMaxPrice(user.email(), max_price, dog_id_and_type[1])
			data['dog_walkers']= filter.getByMaxPrice()
		
		data['available'] = filter.calculateAvailable() #calculate available dogwalkers
		data['row_count'] = filter.getRowCount() #get number of rows --> number of matched dogwalkers
		
		#### PREPARE RESULT ####
		template = jinja_environment.get_template('dog_registration_with_walker.html')
		self.response.write(template.render(data))
		#############

# -------------------
# This class handles the registration process of a dog that belong to a dog owner,
# to a dog walker. The dog walker was found by the class "ShowByFilter" to prevent
# dog registration with a dog walker in full capacity.
# Handles '/owner/profile/registerdog'
# ------------------------			
class DogRegistrationWithWalker(webapp2.RequestHandler):
	@login_required
	def get(self): #when the user accidentally enters this url
		user = users.get_current_user() # get current user connection status
		result = checks.recognize_person(user.email())
		if result == 3: # a dog walker entered dog owner zone
			return self.redirect('/walker/profile') #redirect dog walker to his profile page
		
		return self.redirect('/owner/profile/filter') #else, return to the filter page.
	
	def post(self): 
		user = users.get_current_user() # get current user connection status
		data = self.request.get('data') # get all relevant data from the form
		logging.info("data contains: "+str(data))
		data = data.split(",")
		
		#### COMMIT DOG REGISTRATION WITH WALKER ####
		result = registration.register_dog(data)
		
		### DOG REGISTRATION STATUS ###
		if result:# will be false in case the registration failed
			logging.info("dog registration was successful")
			status = {'data': 1} #registration success
		else:
			logging.info("dog registration fail")
			status = {'data': 2} #registration failed
		
		#### PREPARE REGISTRATION RESULT ####
		template = jinja_environment.get_template('add_a_dog_status.html')
		return self.response.write(template.render(status))


# -------------------
# This class handles the request of a dog owner to view the assigned Dog Walkers.
# Handles '/owner/profile/assignedwalkers'
# ------------------------			
class ShowDogWalkersForDogOwner(webapp2.RequestHandler):
	@login_required
	def get(self):
		user = users.get_current_user() # get current user connection status
		result = checks.recognize_person(user.email())
		if result == 3: # a dog walker entered dog owner zone
			return self.redirect('/walker/profile') #redirect dog walker to his profile page
		
		data_from_db = profile.getRelevantDogWalkers(user.email())
		data = {
		'dog_walkers': data_from_db[0], #retrieve assigned dog walkers
		'total_cost': data_from_db[1], #retrieve total cost of dog owner
		'row_count': data_from_db[2], #retrieve number of rows received by query --> number of assigned dog walkers
		'days': profile.days}
		logging.info(str(data))
		
		### PREPARE RESPONSE ###
		template = jinja_environment.get_template('dog_owner_relevant_dogwalkers.html')
		self.response.write(template.render(data))
		

##############################################################################
#################################            #################################
################################# DOG WALKER #################################
#################################            #################################
##############################################################################

# -------------------
# This class handles the dog owner profile page.
# Handles '/walker/profile'
# ------------------------	
class ProfileDogWalker(webapp2.RequestHandler):
	@login_required
	def get(self):
		user = users.get_current_user() # get current user connection status
		result = checks.recognize_person(user.email())
		if result == 1 or result == 2: # a dog owner entered dog owner zone
			return self.redirect('/owner/profile') #redirect dog owner to his profile page
		elif result == 0:
			return self.redirect('/') #in case the person does not exist in database
		
		
		data = profile.walker_main_page(user.email())#prepare the data for the dog walker profile
		template = jinja_environment.get_template('profile_dogwalker.html')
		self.response.write(template.render(data))

		
# -------------------
# This class handles the dog owner profile page.
# Handles '/walker/profile/schedule'
# ------------------------	
class ShowWalkerSchedule(webapp2.RequestHandler):
	@login_required
	def get(self):
		user = users.get_current_user() # get current user connection status
		result = checks.recognize_person(user.email())
		if result == 1 or result == 2: # a dog owner entered dog owner zone
			return self.redirect('/owner/profile') #redirect dog owner to his profile page
		elif result == 0:
			return self.redirect('/') #in case the person does not exist in database
		
		data = profile.walker_schedule(user.email()) #receive the relevant data for dog walker schedule
		template = jinja_environment.get_template('profile_dogwalker_schedule.html')
		self.response.write(template.render(data))			

	
# -------------------------------------------------------------
# define the relevant URL and the connection to the relevant
# classes, as they are described above.
# -------------------------------------------------------------
app = webapp2.WSGIApplication([	('/',		MainPage),
								('/login', Login),
								('/logout', Logout),
								('/registerdogowner', DogOwner),
								('/registerdogwalker', DogWalker),
								('/owner/profile', ProfileDogOwner),
								('/owner/profile/add', AddADog),
								('/owner/profile/filter', ShowByFilter),
								('/owner/profile/registerdog', DogRegistrationWithWalker),
								('/owner/profile/assignedwalkers', ShowDogWalkersForDogOwner),
								('/walker/profile', ProfileDogWalker),
								('/walker/profile/schedule', ShowWalkerSchedule)],
								debug=True)
