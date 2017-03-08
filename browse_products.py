#!/usr/bin/env python3

# Local:
import authentication
from element_ids import *
from helpers import is_int
from errors import category_xpath_error

# External:
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

def get_product_href(product_element):
    """Returns the value of the href attribute within the appropriate child
    of a given selenium web page element"""
    return product_element.find_element_by_class_name(
                                                PRODUCT_PAGE_LINK_CLASS)

def search(browser, search_term, category_index = 0):
    '''
    Initiates a search in the main Amazon search field, with an optional 
    argument specifiying a product category.
    Returns True if successful.
    '''
    use_custom_category = False
    if not category_index == 0:
        use_custom_category = True
        try: 
            cat_select = Select(browser.find_element_by_xpath(
                                          CAT_DROPDOWN_XPATH))
            cat_select.select_by_index(category_index)
        except NoSuchElementException:
            if category_xpath_error(): # returns bool based on user choice
                use_custom_category = False
            else:    
                return False
    try:
        search_field = browser.find_element_by_xpath(SEARCH_FIELD_XPATH)
    except NoSuchElementException:
        print('Stored Xpath does not match search text box element on page.')
        print('Aborting search...')
        return False
    search_field.send_keys(search_term)
    try: 
        submit_button = browser.find_element_by_xpath(SEARCH_SUBMIT_XPATH)
        submit_button.click()
    except NoSuchElementException:
        search_field.send_keys(keys.ENTER)


def choose_category(browser):
    '''
    Provides a command-line interface for choosing a category from Amazon's 
    drop-down list. Returns the index of the chosen category.
    '''
    cat_unselected = True;
    while cat_unselected:
        cat_select = Select(browser.find_element_by_xpath(CAT_DROPDOWN_XPATH))
        cat_options = cat_select.options
        cat_names = []
        print('Select from the following search categories:\n')
        print(' {0:7}{1}'.format('INDEX', 'NAME'))
        #print(' {0:7}{1}'.format('`````', '````'))
        for i in range(len(cat_options)):
            cat_option_text = [' {:7}'.format(str(i))]
            cat_names.append(cat_options[i].get_attribute('innerHTML'))
            cat_names[i] = cat_names[i].replace('&amp;','&')
            cat_option_text.append(cat_names[i])
            print(''.join(cat_option_text))
        print('\nEnter the index of the category you wish to search.')
        user_input = input()
        if is_int(user_input) and 0 <= int(user_input) <= len(cat_options):
            cat_index = int(user_input);
            selected_cat_name = cat_names[cat_index]
            print('You have selected the category: ' + selected_cat_name)
            undecided = True
            while undecided:
                accept = input('Enter Y to accept or N to choose again:\n')
                if accept == 'y' or accept == 'Y':
                    undecided = False
                    cat_unselected = False
                elif accept == 'n' or accept == 'N':
                    undecided = False
                else:
                    print('Input not recognised.')
        else:
            print('Invalid category index!')
            print('Please enter a number between 0 and ' 
                                + str(len(cat_options)))
def shopping_list_add(browser, search_string, number_products, category):
    search(browser, search_string, category)
    current_result = 0
    completed = False
    while not completed:
        try:
            product_element = browser.find_element_by_id(
                                'result_' + str(current_result))
            product_link = get_product_href(product_element)
            try:
                product_link.click()
            except:
                browser.get(product_link.get_attribute('href'))
            
            
        except NoSuchElementException:
            next_page_link = browser.find_element_by_id(NEXT_PAGE_ID)
            
    return None

# TEST CODE
'''browser = webdriver.Chrome()
authentication.sign_in(browser, 'louis.kerley@yandex.com', 'rJUirp8qB64kD7Qs')
shopping_list_add(browser, 'crazy', 44, 37)'''
