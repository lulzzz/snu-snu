#!/usr/bin/env python3

# Local
import data
from helpers import is_int
from helpers import yes_no_input_prompt

# External
import sys
import pickle
import nltk
import string
from nltk.probability import FreqDist 
from nltk import tokenize
from nltk.corpus import stopwords
from nltk.corpus import treebank
from nltk.tag import UnigramTagger

ADDITIONAL_STOPS = ["it's", "i'm", "i'll", "i'd", "i've", 
					"it’s", "i’m", "i’ll", "i’d", "i’ve", 
					"he's", "he'd", "he'll", 
					"he’s", "he’d", "he’ll", 
					"she's", "she'd", "she'll",
					"she’s", "she’d", "she’ll",
					"you're", "you'd", "you've",
					"you’re", "you’d", "you’ve"]
					
PENN_NOUN_TAGS = 		['NP', 'NX', 'NN', 'NNS', 'NNP', 'NNPS']
PENN_PRONOUN_TAGS = 	['PRP', 'PRP$', 'WP', ' WP$']
PENN_VERB_TAGS = 		['VP', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
PENN_ADVERB_TAGS = 		['ADVP', ' WHADJP', ' WHAVP', 'RB', 'RBR', 'RBS', 'ADV'
						'-BNF', '-DIR', '-EXT', '-LOC', '-MNR', '-PRP', '-TMP']
PENN_ADJECTIVE_TAGS = 	['ADJP', ' WHADJP', 'JJ', 'JJR', 'JJS']
PENN_PREPOSITION_TAGS =	['PP', 'WHPP', 'IN']

def frequency_analysis():
	"""
	Performs simple frequency analysis with options for 
	minimum word length, number of words and parts-of-speech to be included.
	"""
	# get trained Unigram tagger
	train_sents = treebank.tagged_sents()
	print('Loading unigram tagger...')
	unigram_tagger = UnigramTagger(train_sents)
			
	
	text_string = data.string_from_text_file(sys.argv[2]).lower()
	chars_to_delete = '",.?()[]<>~!`’–-•—' 
	# translate() takes a dictionary as input. 
	# Dict mapping ordinal chars to None is created in place.
	text_string = text_string.translate({ord(c): None for c in chars_to_delete})
	words = text_string.split() # crude tokenisation, keeps contractions
	english_stops = stopwords.words('english')

	stops_set = set(english_stops + ADDITIONAL_STOPS)
	cleaned_words = []
	for w in words:
		if w not in stops_set and w not in string.punctuation:
			cleaned_words.append(w)
	fdist = FreqDist(cleaned_words)
	#print(english_stops)
	prelim_results = ['\nFrequency analysis had found ']
	prelim_results.append(str(fdist.B()))
	prelim_results.append(' unique words of potential interest\n')
	prelim_results.append('out of a total of ')
	prelim_results.append(str(fdist.N()))
	prelim_results.append('.')
	print(''.join(prelim_results))
	committed = False
	num_words = 100
	min_word_length = 0
	max_word_length = 16
	while not committed:
		intro = ['The ']
		intro.append(str(num_words))
		intro.append(' most frequent words are currently selected.\n')
		intro.append('Selected words are currently between ')
		intro.append(str(min_word_length))
		intro.append(' and ')
		intro.append(str(max_word_length))
		intro.append(' characters in length.\n')
		intro.append('Below are the words included in the current selection:\n')
		print(''.join(intro))
		selected_words = fdist.most_common(num_words)
		word_string = []
		charcount = 0
		for w in selected_words:
			charcount += (len(w[0]) + 2)
			if charcount > 80:
				word_string.append('\n')
				charcount = 0
			word_string.append(w[0])
			word_string.append(', ')
		word_string[len(word_string) - 1] = '\n' # strip comma, add linebreak
		print(''.join(word_string))
		chosen = False
		while not chosen:
			print('Enter M below to change the minimum word length.')			
			print('Enter X below to change the maximum word length.')
			print('Enter N to change the total number of words selected.')
			print('Enter P to restrict selection with part-of-speech tagging.')
			print('Enter A to accept the current list of words and continue.')
			user_input = input()
			if user_input.lower() == 'l':
				value_set = False
				while not value_set:
					new_value = input('\nEnter a new mimimum word length...\n')
					if is_int(new_value):
						min_word_length = int(new_value)
						value_set = True
						chosen = True
					else:
						print('Please enter an integer.')
			elif user_input.lower()  == 'n':
				value_set = False
				while not value_set:
					new_value = input('\nEnter a new number of words...\n')
					if is_int(new_value):
						num_words = int(new_value)
						value_set = True
						chosen = True
					else:
						print('Please enter an integer.')
			elif user_input.lower()  == 'p':
				print("The parts-of-speech tagger is seldom 100% sucessful.")
				print('Do you want to include untagged words?')
				include_untagged = yes_no_input_prompt()
				print('\nDo you want to include nouns?')
				include_nouns = yes_no_input_prompt()
				print('\nDo you want to include pronouns?')
				include_pronouns = yes_no_input_prompt()
				print('\nDo you want to include verbs?')
				include_verbs = yes_no_input_prompt()
				print('\nDo you want to include adverbs?')
				include_adverbs = yes_no_input_prompt()
				print('\nDo you want to include adjectives?')
				include_adjectives = yes_no_input_prompt()
				print('\nDo you want to include prepositions?')
				include_prepositions = yes_no_input_prompt()
				print('\nDo you want to include forms not listed above?')
				include_others = yes_no_input_prompt()
					
			elif user_input == 'A' or user_input == 'a':
				chosen = True
				committed = True
			else:
				print('Input not recognised')
		new_words = []
		cleaned_words_tagged = unigram_tagger.tag(cleaned_words)
		print(cleaned_words_tagged[1:20])
		for w in cleaned_words:
			if len(w) >= min_word_length:
				new_words.append(w)
		fdist = FreqDist(new_words)

# Dictionary of dictionaries defining command arguments accepted by snu-snu
ARGS = {'freq': 
	{'description' : 'derives commands from a text based on frequency analysis',
	'required arg count' : 4,
	'required args' : 
		'   1. the command (i.e. "freq") 2. path to source file (e.g. "in.txt")'
		+ '\n   3. path to destination file (eg. "out.json")',
	'function' : frequency_analysis}}
	
def initialise():
	"""
	Checks arguments and calls appropriate functions.
	"""
	print("""This is text-process: a utility for generating commands for snu-snu
from arbitrary texts using NLP.\n""")

	# Ensures that NLTK data can be stored in the same directory as code
	nltk.data.path.append('./nltk_data/')
	
	proceed_with_args = False
	if len(sys.argv) > 1:
		includes_recognised_arg = False
		for recognised_arg in ARGS.keys():
			if sys.argv[1] == recognised_arg:
				includes_recognised_arg = True
		if includes_recognised_arg:
			print('You ran text-process with the command argument: ' 
														+ sys.argv[1])
			print('This ' + ARGS[sys.argv[1]]['description'])
			if len(sys.argv) == ARGS[sys.argv[1]]['required arg count']:
				proceed_with_args = True
			else:
				error = ['Error: this command will only work with a total of ']
				error.append(str(ARGS[sys.argv[1]]['required arg count'] - 1))
				error.append(' arguments.')
				print(''.join(error))
				print('See "' + sys.argv[1] + '" in the below list...\n')
				output_command_arguments()
		else:
			print('Command argument "' + sys.argv[1] + '" not recognised\n')
			output_command_arguments()
	else:
		print('Error: text-process requires terminal arguments to run.\n')
		output_command_arguments()
	if proceed_with_args:
		ARGS[sys.argv[1]]['function']()
	else: 
		print('Quitting...')
		quit()

def output_command_arguments():
	print('These are the recognised command arguments:')
	print(' {0:10}{1}'.format('NAME', 'DESCRIPTION'))
	for a in ARGS.keys():
		print(' {0:10}{1}'.format(a, ARGS[a]['description']))
		print('   Required arguments:')
		print(ARGS[a]['required args'] + '\n')

initialise()
