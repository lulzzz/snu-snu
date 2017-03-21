#!/usr/bin/env python3

# Local:
import authentication
import browse_products
from element_ids import *
from helpers import is_int
from errors import category_xpath_error

# External:
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import TimeoutException


def get_product_link(product_element):
    """Returns the link element inside a product listing element"""
    try:
        return product_element.find_element_by_class_name(
                                                PRODUCT_PAGE_LINK_CLASS)
    except NoSuchElementException:
        print('Unable to find product page link. Skipping item.')
        return None

def go_home(browser):
    try:
        logo_link = browser.find_element_by_id(NAV_LOGO_ID)
        logo_link.click()
    except NoSuchElementException:
        browser.get(AMAZON_URL)

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
    return True


def choose_category(browser):
    '''
    Provides a command-line interface for choosing a category from Amazon's
    drop-down list. Returns the index of the chosen category.
    '''
    cat_index = 0
    cat_unselected = True
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
            cat_unselected = False
        else:
            print('Invalid category index!')
            print('Please enter a number between 0 and '
                                + str(len(cat_options)))
    return cat_index

def view_items(browser, search_string, number_products, category,
                                            item_function = None):
    search(browser, search_string, category)
    current_result = 0
    completed = False
    while not completed:
        product_elements = browser.find_elements_by_id(
                            'result_' + str(current_result))
        if(len(product_elements) > 0):
            product_link = get_product_link(product_elements[0])
            if not product_link == None:
                try:
                    product_link.click()
                except:
                    print('Could not click product element. Manually getting link.')
                    browser.get(product_link.get_attribute('href'))
                # If present, call a function to do something on the product page
                if not item_function == None:
                    try:
                        item_function(browser)
                    except TimeoutException:
                        print('Failed to add item to list. Item page timed out')
                browser.back()
        else:
            next_page_links = browser.find_elements_by_id(NEXT_PAGE_LINK_ID)
            if len(next_page_links) > 0:
                sucessful = False
                try:
                    next_page_text = browser.find_element_by_id(NEXT_PAGE_STRING_ID)
                    next_page_text.click()
                    successful = True
                except NoSuchElementException:
                    print('Error: next page link not found.')
                except ElementNotVisibleException:
                    print('Error: next page link not visible.')
                except WebDriverException:
                    print('Unknown error in navigating to next result page.')
                if not successful:
                    try:
                        next_page_arrow = browse.find_element_by_xpath(
                                                    NEXT_PAGE_ARROW_XPATH)
                        next_page_arrow.click()
                        successful = True
                    except NoSuchElementException:
                        print('Error: next page arrow not found.')
                    except ElementNotVisibleException:
                        print('Error: next page arrow not visible.')
                    except WebDriverException:
                        print('Unknown error in navigating to next result page.')
                if not successful:
                    try:
                        browser.get(next_page_links[0].get_attribute('href'))
                        successful = True
                    except WebDriverException:
                        print('Error: failed to navigate to next result page')


                if not successful:
                    end_string = ['End of results reached for search: "']
                    end_string.append(search_string)
                    end_string.append('". Only ')
                    end_string.append(str(current_result - 1))
                    end_string.append(' of the specified ')
                    end_string.append(str(number_products))
                    end_string.append(' products viewed.')
                    print(''.join(end_string))
                    completed = True


        current_result += 1
        if current_result > number_products:
            completed = True


def add_item_list(browser) :
    try:
        list_add_button = browser.find_element_by_id(ADD_TO_LIST_BUTTON_ID)
        list_add_button.click()
    except NoSuchElementException:
        print('Failed to add item to list. No button on page found matching '
                + 'stored element ids.')
    except ElementNotVisibleException:
        print('Failed to add item to list. List add button is not visible.')


# TEST CODE
'''browser = webdriver.Chrome()
authentication.sign_in(browser, 'louis.kerley@yandex.com', 'rJUirp8qB64kD7Qs')
view_items(browser, 'fuck', 160, 40)'''
