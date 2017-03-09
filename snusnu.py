#!/usr/bin/env python3

# Local:
import authentication
import browse_products
from helpers import is_int


# External:
from selenium import webdriver
import getpass
from enum import Enum

class ProductAction(Enum):
	search = 0
	view = 1
	add_shopping_list = 2

class Command():
	'''Used as a parent class for all commands and 
		to represent generic descriptions of commands'''
	def __init__(self, name, description, associated_action = None):
		self.name = name
		self.description = description
		self.associated_action = associated_action

class ProductCommand(Command):
	def __init__(self, name, description, associated_action,
						search_category, search_string, number_of_items):
		super(ProductCommand, self).__init__(name, description, 
											associated_action)
		self.search_string = search_string
		self.number_of_items = number_of_items
		self.search_category = search_category

COMMANDS = [Command('search',
			'Carry out a single product search.',
			ProductAction.search),
			Command('view',
			'View products matching a search.',
			ProductAction.view),
			Command('listadd',
			'Add products matching a search term to the default wishlist.',
			ProductAction.add_shopping_list),
			Command('execute', 'Execute all queued commands.'),
			Command('exit', 'Quit snu-snu.')]

def initialise():
	"""Performs initilisation and Amazon authentication"""
	
	print("""Welcome to snu-snu: the utility that takes the hard
 work out of training Amazon's recommendation algorithm.\n""")
	print("""you will now be asked for the email address and password for the
Amazon account you wish to train...\n""")
	authenticated = False
	while not authenticated:
		email = input('Please enter the email address used for Amazon...\n')
		password = getpass.getpass("Please enter the password...\n")
		browser = webdriver.Chrome() # May need browser selection at later date
		if authentication.sign_in(browser, email, password):
			authenticated = True
		else:
			browser.quit()
			print('Authentication failed. do you want to try again?')
			decided = False
			while not decided:
				decision = input('Please enter Y or N...\n')
				if decision == 'y' or decision == 'Y':
					print('Retrying...')
					decided = True
				elif decision == 'n' or decision == 'N':
					print('Snu-snu requires Amazon authentication. Quitting...')
					exit()
				else:
					print('Input not recognised!')
	run(browser)
					
def run(browser):
	running = True
	queued_commands = []
	while running:
		print('Below is a list of avaliable commands:\n')
		print(' {0:10}{1}'.format('NAME', 'DESCRIPTION'))
		#print(' {0:10}{1}'.format('####', '###########'))
		for c in COMMANDS:
			print(' {0:10}{1}'.format(c.name, c.description))

		if len(queued_commands) > 0:
			current_commands_msg = ['\n(There are currently ']
			current_commands_msg.append(str(len(queued_commands)))
			current_commands_msg.append(' commands queued.)')
			print(''.join(current_commands_msg))
		awaiting_command = True
		selected_command = None
		while awaiting_command:
			user_cmd = input('\nPlease enter the name of a command...\n')
			for c in COMMANDS:
				if user_cmd == c.name:
					selected_command = c
					awaiting_command = False
			if awaiting_command:
				print('Command not recognised!')
		if selected_command.name == 'execute':
			if len(queued_commands) > 0:
				if execute_commands(browser, queued_commands):
					print('Command(s) executed sucessfully.')
				else:
					print('Commands(s) executed with one or more errors.')
				decided = False
				while not decided:
					user_decision = input('Do you wish to issue further commands?'
								+ '\nPlease enter Y or N...\n')
					if user_decision == 'n' or user_decision == 'N':
						print('Quitting...')
						exit()
					elif user_decision == 'y' or user_decision == 'Y':
						queued_commands = []
						decided = True
					else:
						print('Input not recognised!')
			else:
				print('Error: there are no commands in the queue to execute.\n')
		elif selected_command.name == 'exit':				
			decided = False
			while not decided:
				user_decision = input('Do you really want to quit snu-snu?'
							+ '\nPlease enter Y or N...\n')
				if user_decision == 'y' or user_decision == 'Y':
					print('Quitting...')
					exit()
				elif user_decision == 'n' or user_decision == 'N':
					print('Continuing...')
				else:
					print('Input not recognised!')

		else: 
			intro = ['']
			intro.append('The selected command "')
			intro.append(selected_command.name)
			intro.append('" will do the following: ')
			intro.append(selected_command.description)
			print(''.join(intro))
			print('Please enter the search term to use when finding products.')
			search_term = input()
			category_number = browse_products.choose_category(browser)		
			number_of_products = 0
			if not selected_command.name == 'search':
				print('How many products should the command be executed on?')
				valid_int = False
				while not valid_int:
					product_count = (input())
					if is_int(product_count):
						number_of_products = int(product_count)
						valid_int = True
					else:
						print("That wasn't a valid integer. Please re-enter...")
			
			full_command = ProductCommand(selected_command.name,
										selected_command.description,
										selected_command.associated_action,
										category_number,
										search_term,
										number_of_products)
			queued_commands.append(full_command)
			success = []
			success.append('Command "')
			success.append(full_command.name)
			success.append('" sucessfully added to the queue!')
			success.append('\nEnter the "execute" command to carry it out.\n')
			print(''.join(success))

def execute_commands(browser, command_list):
	""" Executes a list of commands defined by Command objects. Returns True
	if completely succesful"""
	error_has_occured = False
	for c in command_list:
		if c.associated_action == ProductAction.search:
			print('made it to if block!')
			if not browse_products.search(browser, 
									c.search_string, 
									c.search_category):
				error_has_occured = True

		elif c.associated_action == ProductAction.view:
			if not browse_products.view_items(browser, 
										c.search_string, 
										c.number_of_items,
										c.search_category):
				error_has_occured = True

		elif c.associated_action == ProductAction.add_shopping_list:
			if not browse_products.view_items(browser, 
										c.search_string, 
										c.number_of_items,
										c.search_category,
										browse_products.add_item_list):
				error_has_occured = True
		browse_products.go_home(browser)
	if error_has_occured:
		return False
	else:
		return True

initialise()
