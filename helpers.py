def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def is_float(value):    
    try:
        float(value)
        return True
    except ValueError:
        return False

def yes_no_input_prompt():
	decided = False
	while not decided:
		user_input = input('Enter Y or N...\n')
		if user_input.lower() == 'y':
			return True
		elif user_input.lower() == 'n':
			return False
		else:
			print('Input not recognised')

def int_input_prompt(message):
	value_set = False
	while not value_set:
		new_value = input(message)
		if is_int(new_value):
			return int(new_value)git co
		else:
			print('Please enter an integer.')
			
	
