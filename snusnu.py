#!/usr/bin/env python3

# Local:
import errors
import authentication
import data
import browse_products
from helpers import is_int
from helpers import yes_no_input_prompt
from helpers import int_input_prompt

# External:
import sys
import json
from selenium import webdriver
import getpass
from enum import Enum


ATTEMPTED_SET_DEFAULT_LIST = False
print('Default list flag has been set. Its value is: ' + str(ATTEMPTED_SET_DEFAULT_LIST))

COMMANDS = [data.Command('search',
			'Carry out a single product search.',
			data.ProductAction.search),
			data.Command('view',
			'View products matching a search.',
			data.ProductAction.view),
			data.Command('listadd',
			'Add products matching a search term to the default wishlist.',
			data.ProductAction.add_shopping_list),
			data.Command('execute', 'Execute all queued commands.'),
			data.Command('exit', 'Quit snu-snu.')]

def json_input(browser):
	"""
	attempts to get JSON representations of commands from a path specified 
	as an argument and execute all of them.
	"""
	commands = data.product_commands_from_file(sys.argv[2])
	execute_commands(browser, commands)

# Dictionary of dictionaries defining command arguments accepted by snu-snu
ARGS = {'input': 
			{'description' : 'attempts to exceute commands from a JSON file.',
			'required arg count' : 3, 
			'function' : json_input}}

def initialise():
	"""
	Checks arguments and decides whether or not to use the default interface.
	"""
	print("""Welcome to snu-snu: the program that takes the hard work out of 
training Amazon's recommendation algorithm.\n""")
	proceed_with_args = False
	if len(sys.argv) > 1:
		includes_recognised_arg = False
		for recognised_arg in ARGS.keys():
			if sys.argv[1] == recognised_arg:
				includes_recognised_arg = True
		if includes_recognised_arg:
			print('You ran snu-snu with the argument: ' + sys.argv[1])
			print('This ' + ARGS[sys.argv[1]]['description'])
			if len(sys.argv) == ARGS[sys.argv[1]]['required arg count']:
				print('Snu-snu will process your arguments after Amazon login.\n')
				proceed_with_args = True
			else:
				error = ['Error: this argument will only work with a total of ']
				error.append(str(ARGS[sys.argv[1]]['required arg count'] - 1))
				error.append(' arguments.')
				print(''.join(error))
				print('Do you wish to go to the default snu-snu interface anyway?')
				if yes_no_input_prompt():
					print('Continuing...')
				else:
					print('Quitting...')
					quit()
						
	# Tries to get an authenticated browser
	browser = authenticate()

	if proceed_with_args:
		ARGS[sys.argv[1]]['function'](browser)
	else:
		run(browser)
	
def authenticate():
	""" 
	Attempts to sign into Amazon and return a webdriver object if successful 
	"""
	print("""You will now be asked for the email address and password for the
Amazon account you wish to train...\n""")

	authenticated = False
	while not authenticated:
		email = input('Please enter the email address used for Amazon...\n')
		password = getpass.getpass("Please enter the password...\n")
		browser = webdriver.Chrome() # May need browser selection at later date
		if authentication.sign_in(browser, email, password):
			authenticated = True
			return browser
		else:
			browser.quit()
			print('Authentication failed. do you want to try again?')
			if yes_no_input_prompt():
				print('Retrying...')			
			else:
				print('Snu-snu requires Amazon authentication. Quitting...')
				exit()

def run(browser):
	running = True
	queued_commands = []
	while running:
		print('Below is a list of avaliable commands:\n')
		print(' {0:10}{1}'.format('NAME', 'DESCRIPTION'))
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
					print('Do you wish to issue further commands?')
					if yes_no_input_prompt():
						queued_commands = []
						decided = True
					else:
						print('Quitting...')
						exit()
			else:
				print('Error: there are no commands in the queue to execute.\n')
		elif selected_command.name == 'exit':
			print('Do you really want to quit snu-snu?')
			if yes_no_input_prompt():
				print('Quitting...')
				exit()
			else:
				print('Continuing...')

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
				number_of_products = int_input_prompt('How many products should'
										+	' the command be executed on?\n')

			full_command = data.ProductCommand(selected_command.name,
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
	""" 
	Executes a list of commands defined by Command objects. Returns True
	if completely succesful
	"""
	error_has_occured = False
	for c in command_list:
		if c.associated_action == data.ProductAction.search:
			if not browse_products.search(browser,
									c.search_string,
									c.search_category):
				error_has_occured = True

		elif c.associated_action == data.ProductAction.view:
			if not browse_products.view_items(browser,
										c.search_string,
										c.number_of_items,
										c.search_category):
				error_has_occured = True

		elif c.associated_action == data.ProductAction.add_shopping_list:
			global ATTEMPTED_SET_DEFAULT_LIST
			if not ATTEMPTED_SET_DEFAULT_LIST:
				print("It is possble that the default list is not set.")
				print('Attempting to set default list to "Shopping list"...')
				if browse_products.set_shopping_list_default(browser):
					print('"Shopping list" either already default ' +
									'or succesfully set to default.')
				else:
					print('Failed to set "Shopping list" to default!')
					print('It may be necessary to set it manaully.')
				ATTEMPTED_SET_DEFAULT_LIST = True
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
def test():
	fudge_command = data.ProductCommand('listadd',
			'Add products matching a search term to the default wishlist.',
										data.ProductAction.add_shopping_list,
										0,
										'fudge',
										1337)
	print(json.dumps(fudge_command, cls=data.ProductCommandEncoder))
	data.product_commands_to_file([fudge_command], 'fudge.json')
#test()
initialise()
