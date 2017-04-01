# Local
from element_ids import *
from helpers import keep_strings_matching
import data
import authentication

# External
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import WebDriverException
from selenium import webdriver

def get_recommendations(browser, number_of_recommendations):
	""" Assumes Amazon user is authenticated.
		Gets a specified number of recommendations """
	print('Navigating to recommendations...')
	# First phase of navigating to recommendations
	successful = False
	try:
		your_amazon_button = browser.find_element_by_id(NAV_YOUR_AMAZON_ID)
		your_amazon_button.click()
		successful = True
	except ElementNotVisibleException:
		print('Error: element used to navigate to "your Amazon" not visible.')
	except NoSuchElementException:
		print('Error: element used to navigate to "your Amazon" not found.')
	if not successful:
		try:
			recommendations_link = browser.find_element_by_xpath(
											MENU_YOUR_RECOMMENDATIONS_XPATH)
			browser.get(str(recommendations_link.get_attribute('href')))
			successful = True
		except ElementNotVisibleException:
			print('Error: element used to navigate to "your Amazon" not visible.')
		except NoSuchElementException:
			print('Error: element used to navigate to "your Amazon" not found.')
	if not successful:
		print('Failure: unable to navigate to "your Amazon". Check element ids.')
		return None
	# Second phase of navigating to recommendations
	successful = False
	try:
		recommendations_link = browser.find_element_by_xpath(
												NAV_RECOMMENDED_FOR_YOU_XPATH)
		recommendations_link.click()
		successful = True
	except ElementNotVisibleException:
		print('Error: element used to navigate to recommendations not visible.')
		print('Trying to navigate to the link directly...')
		try:
			browser.get(str(recommendations_link.get_attribute('href')))
			sucessful = True
		except:
			print('Error: failed to follow link to recommendations')
	except NoSuchElementException:
		print('Error: element used to navigate to recommendations not found.')
	if not successful:
		print('Failure: unable to navigate to recommendations. Check element ids.')
		return None
		
	# Scrape the recommendations
	scraped_names = []
	scraped_images = []
	scraped_prices = []
	recommendations_scraped = 0
	while recommendations_scraped < number_of_recommendations:
		names = browser.find_elements_by_xpath(PARTIAL_PRODUCT_NAME_XPATH)
		print ('Selenium found ' + str(len(names)) + ' product name elements')
		names_text = []
		for n in names:
			names_text.append(n.get_attribute('innerHTML'))
		for n in names_text:
			n = n.replace('<strong>', '')
			n = n.replace('</strong>', '')
			print(n)
		images = browser.find_elements_by_xpath(PARTIAL_PRODUCT_IMAGE_XPATH)
		image_urls = []
		for i in images:
			image_urls.append(i.get_attribute('src'))
		image_data = []
		i = 0
		for u in image_urls:
			image_data.append(data.base_64_gif_from_web(u))
			i += 1
		print ('Selenium found ' + str(len(images)) + ' product image elements')
		prices = browser.find_elements_by_class_name(PRICE_SPAN_CLASS)
		print ('Selenium found ' + str(len(prices)) + ' product price elements')
		prices_text = []
		for p in prices:
			prices_text.append(p.get_attribute('innerHTML'))
		prices_text = keep_strings_matching(prices_text, ['<b>', '</b>'])
		print('Product price elements have been reduced in number to ' 
											+ str(len(prices_text)))
		for p in prices_text:
			p = p.replace('<b>', '')
			p = p.replace('</b>', '')
			print(p)
		scraped_names.append(names_text)
		scraped_images.append(image_data)
		scraped_prices.append(prices_text)
		recommendations_scraped += len(names)
		# Navigate to next page of recommendations
		successful = False	
		try:
			more_results_button = browser.find_element_by_id(
													MORE_RESULTS_BUTTON_ID)
			more_results_button.click()
			successful = True
		except WebDriverException:
			print('Possible error clicking more results button. '
					+ ' Trying parent element...')
		if not successful:
			try:
				more_results_button = browser.find_element_by_id(
														MORE_RESULTS_BUTTON_ID)
				more_results_link = more_results_button.find_element_by_xpath('..')
				more_results_link.click()
				successful = True
			except WebDriverException:
				try:
					print('Possible error finding "more results" link. '
							+ 'Trying alternative xpath...')
					more_results_link = browser.find_element.by.xpath(
													MORE_RESULTS_LINK_XPATH)
					more_results_link.click()
					successful = True
				except WebDriverException:
					print('Error clicking element based on alternative xpath')
		if not successful:
			

	recommended_products = []
	for i in range(len(number_of_recommendations)):
		recommended_products.append(data.ProductDescription(scraped_names[i],
															scraped_prices[i],
															scraped_images[i]))
	return recommended_products
	
def test():
	browser = webdriver.Chrome()
	authentication.sign_in(browser, 'cool.s.dedalus@yandex.com', '64M[gzXBe"~R*%-')
	recommendations = get_recommendations(browser, 500)
	data.product_descriptions_to_file(recommendations, 'joyce_recommendations.json')
	
test()