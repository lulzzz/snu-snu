#!/usr/bin/env python3

# Local:
import snusnu.authentication as authentication
from snusnu.element_ids import *
from snusnu.helpers import is_int
from snusnu.errors import category_xpath_error

# External:
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException


def get_product_link(product_element):
    """Returns the link element inside a product listing element"""
    try:
        return product_element.find_element_by_class_name(
                                                PRODUCT_PAGE_LINK_CLASS)
    except NoSuchElementException:
        print('Unable to find product page link. Skipping item.')
        return None

def go_home(drv):
    try:
        logo_link = drv.find_element_by_id(NAV_LOGO_ID)
        logo_link.click()
    except NoSuchElementException:
        drv.get(AMAZON_URL)

def search(drv, search_term, category_index = 0):
    '''
    Initiates a search in the main Amazon search field, with an optional
    argument specifiying a product category.
    Returns True if successful.
    '''
    print('Searching for "' + search_term + '"...')
    use_custom_category = False
    if not category_index == 0:
        use_custom_category = True
        try:
            cat_select = Select(drv.find_element_by_xpath(
                                          CAT_DROPDOWN_XPATH))
            cat_select.select_by_index(category_index)
        except NoSuchElementException:
            if category_xpath_error(): # returns bool based on user choice
                use_custom_category = False
            else:
                return False
    try:
        search_field = drv.find_element_by_xpath(SEARCH_FIELD_XPATH)
    except NoSuchElementException:
        print('Stored Xpath does not match search text box element on page.')
        print('Aborting search...')
        return False
    search_field.send_keys(search_term)
    try:
        submit_button = drv.find_element_by_xpath(SEARCH_SUBMIT_XPATH)
        submit_button.click()
    except NoSuchElementException:
        search_field.send_keys(keys.ENTER)
    return True

def choose_category(drv):
    '''
    Provides a command-line interface for choosing a category from 
    Amazon's drop-down list. Returns the index of the chosen category.
    '''
    cat_index = 0
    cat_unselected = True
    while cat_unselected:
        cat_select = Select(drv.find_element_by_xpath(
													CAT_DROPDOWN_XPATH))
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
        if is_int(user_input) 
        and 0 <= int(user_input) 
        <= len(cat_options):
            cat_index = int(user_input);
            selected_cat_name = cat_names[cat_index]
            cat_unselected = False
        else:
            print('Invalid category index!')
            print('Please enter a number between 0 and '
                                + str(len(cat_options)))
    return cat_index

def set_shopping_list_default(drv):
    """
    WARNING: Not functional. Intended to set default wishlist
    to "shopping list" from
    """
    print('Attempting to navigate to "Lists"...')
    successful = False
    try:
        lists_link_button = drv.find_element_by_id(WISHLISTS_LINK_ID)
        lists_link_button.click()
        successful = True
        print('Success!')
    except NoSuchElementException:
        print('Error: no "lists" link element found matching stored ID.')
    except ElementNotVisibleException:
        print('Error: "Lists" link identified by stored ID not visible.')
        print('Trying getting the link directly...')
        try:
            drv.get(lists_link_button.get_attribute('href'))
            successful = True
            print('Success!')
        except WebDriverException:
            print('Error failed to navigate to "Lists" page.')
    if not successful:
        try:
            print('Trying to get the "lists" link from the menu...' )
            lists_menu_link = drv.find_element_by_xpath(
                                    WISHLISTS_MENU_LINK_XPATH)
            drv.get(lists_menu_link.get_attribute('href'))
            print('Success!')
        except NoSuchElementException:
            print('Error: no "lists" link element found matching ' 
					+ 'stored XPATH.')
            return False
        except WebDriverException:
            print('Error failed to navigate to "Lists" page.')
            return False

    print('Trying to open "Lists" settings...')
    try:
        settings_link = drv.find_element_by_xpath(
                        WISHLISTS_SETTINGS_LINK_XPATH)
        settings_link.click()
        print('Success!')
    except NoSuchElementException:
        print('Error: No "Lists" settings button found matching'  
				+ 'stored XPATH.')
        return False
    except ElementNotVisibleException:
        print('Error: "Lists" settings button not visible.')
        return False
    except WebDriverException:
        print('Unknown error in finding or clicking "Lists"' 
									+ 'settings button.')
        return False

    print('Trying to select "Shopping list" as default...')
    try:

        # MAY NEED TO ASK SELENIUM TO WAIT UNTIL SELECT IS VISIBLE
        shopping_list_default_select = drv.find_element_by_xpath(
                            WISHLISTS_SHOPPING_DEFAULT_SELECT_XPATH)
        shopping_list_default_select.click()
        print('Success!')
    except NoSuchElementException:
        print('Error: No "Shopping list" select found matching '
											+ 'stored XPATH.')
        return False
    except ElementNotVisibleException:
        print('Error: "Shopping list" select not visible.')
        return False
    except WebDriverException:
        print('Unknown error in finding or clicking "Shopping list"' 
													+ ' select.')
        return False

    print('Trying to submit chanes to settings...')
    try:
        settings_submit_button = drv.find_element_by_xpath(
                            WISHLISTS_SETTINGS_SUMBIT_BUTTON_XPATH)
        settings_submit_button.click()
        print('Success!')
    except NoSuchElementException:
        print('Error: No "submit" button found matching stored XPATH.')
        return False
    except ElementNotVisibleException:
        print('Error: "submit" button not visible.')
        return False
    except WebDriverException:
        print('Unknown error in finding or clicking "submit" button.')
        return False
    return True

def view_items(drv, search_string, number_products, category,
                                            item_function = None):
    search(drv, search_string, category)
    drv.set_page_load_timeout(30)
    current_result = 0
    completed = False
    while not completed:
        product_elements = drv.find_elements_by_id(
                            'result_' + str(current_result))
        # Is there a product element
        # matching the desired on the page?
        if(len(product_elements) > 0):
            product_page_url = drv.current_url
            try:
                product_link = get_product_link(product_elements[0])
                if not product_link == None:
                    try:
                        product_link.click()
                    except:
                        print('Could not click product element. ' +
                                        ' Manually getting link.')
                        drv.get(product_link.get_attribute('href'))
                    # If present, call a function to
                    # do something on the product page
                    if not item_function == None:
                        item_function(drv)
                    drv.get(product_page_url) # possibly more robust
                                                  # than drv.back()
            except TimeoutException:
                print('Item page timed out. ' +
                        'Returning to product page...')
        else:
            next_page_links = drv.find_elements_by_id(NEXT_PAGE_LINK_ID)
            if len(next_page_links) > 0:
                successful = False
                try:
                    next_page_text = drv.find_element_by_id(
													NEXT_PAGE_STRING_ID)
                    next_page_text.click()
                    successful = True
                except NoSuchElementException:
                    print('Error: next page link not found.')
                except ElementNotVisibleException:
                    print('Error: next page link not visible.')
                except WebDriverException:
                    print('Unknown error in navigating to next '
												+ 'result page.')
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
                        print('Unknown error in navigating to next' + 
													' result page.')
                if not successful:
                    try:
                        drv.get(next_page_links[0].get_attribute('href'))
                        successful = True
                    except WebDriverException:
                        print('Error: failed to navigate to next ' 
													+ 'result page')


                if not successful:
                    end_string =['End of results reached for search: "']
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


def add_item_list(drv) :
    # NEEDS CODE TO TEST IF DEFAULT LIST HAS BEEN CHOSEN
    # AND SELECT SHOPPING LIST IF NEEDED
    try:
        list_add_button = drv.find_element_by_id(ADD_TO_LIST_BUTTON_ID)
        list_add_button.click()
    except NoSuchElementException:
        print('Failed to add item to list. No button on page found '
							+'matching stored element ids.')
    except ElementNotVisibleException:
        print('Failed to add item to list. '
				+ 'List add button is not visible.')
