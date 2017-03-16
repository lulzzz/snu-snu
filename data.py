import json
import enum
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

class ProductCommandEncoder(json.JSONEncoder):
    """
    Outputs a JSON representation of a ProductCommand
    """
    def default(self, obj):
        if isinstance(obj, ProductCommand):
            return {'Name' : obj.name,
                'Description' :  obj.description,
                'Associated action' : obj.associated_action.value,
                'Search string' : obj.search_string,
                'Number of items' : obj.number_of_items,
                'Search category' : obj.search_category}
        return json.JSONEncoder.default(self, obj)
        
def parse_product_command(obj):
	'''imports a json representation of a ProductCommand'''	 
	if 'Search category' in obj: 	# rather than identifiying each
									# ProductCommand as such
		return ProductCommand(	obj['Name'],
								obj['Description'],
								ProductAction(obj['Associated action']),
								obj['Search category'],
								obj['Search string'],
								obj['Number of items'])

def product_commands_to_file(commands, path):
	with open(path, 'w') as outfile:
		json.dump(commands, outfile, cls=ProductCommandEncoder)
	
def product_commands_from_file(path):
	with open(path, 'r') as data_file:
		return json.load(data_file, object_hook=parse_product_command)
