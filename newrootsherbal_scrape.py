from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import sys


#launch url
url = "https://newrootsherbal.ca/en/products/"

#create a new chrome session
driver = webdriver.Chrome(r'C:\Users\hemaa\Downloads\chromedriver_win32 (1)\chromedriver.exe')
driver.implicitly_wait(30)
driver.get(url)

soup_level1 = BeautifulSoup(driver.page_source, 'html.parser')

"""for category in soup_level1.find_all('option'):
    print(category.get_text())"""

#BeautifulSoup grabs all products link specific to that category
count = 0
for div in soup_level1.find_all('div', {'class': 'product-list__item'}):
    print("Inside for loop")
    link = div.find('a', {'class': 'product-list__item__link'})
    print(link.get('href'))
    a_link = link.get('href')
    python_button = driver.find_element_by_xpath("//a[@href="+"'"+a_link+"'"+"]")
    driver.implicitly_wait(50)
    print("about to click")
    driver.execute_script("arguments[0].click();", python_button)
    print("Inside the product page")

    driver.switch_to.window(driver.window_handles[1])#locate the first new page (handles)
    soup_level2 = BeautifulSoup(driver.page_source, 'html.parser')

    #-------------Product Name----------------
    product_name = soup_level2.find('h1')
    print("Product Name: ", product_name.get_text())

    #-------------NPN-------------------------
    npn = soup_level2.find('div', {'class': 'product__properties__npn'})
    print("NPN: ", npn.get_text()[5:])

    #------------Format-----------------------
    format = soup_level2.find('div', {'class': 'product__properties__format'})
    print("Format: ", format.get_text()[8:])


    #------------Short Description-------------
    short_descr_div = soup_level2.find('div', {'class': 'product__description__short'})
    list_of_p = short_descr_div.find_all('p')
    short_description = list_of_p[1]
    print("Short Description:\n\t", short_description.get_text())

    #-------------Full Description-------------
    full_descr_div = soup_level2.find('div', {'class': 'product__description__full'})
    full_description = ''
    for p in full_descr_div.find_all('p'):
        full_description += p.get_text()
    print("Full Description:\n\t ", full_description)

    #-------------Directions of use--------------
    directions_of_use_div = soup_level2.find('div', {'class': 'product__use'})
    directions_of_use = ''
    for p in directions_of_use_div.find_all('p'):
        directions_of_use += p.get_text()
    print("Directions of use:\n\t ", directions_of_use)



    #-------------Ingredients------------
    ingr_table = soup_level2.find('table')
    ingr_used = []
    string = ''
    for tr in ingr_table.tbody.find_all('tr'):
        for td in tr.find_all('td'):
            string += td.get_text()
        ingr_used.append(string)
        string = ''
    print("Ingredients used:\n\t", ingr_used)



    #---------------Available Sizes--------------------
    size_tab = soup_level2.find_all('div', {'class': 'tab'})
    for tab_row in size_tab:
        cols = tab_row.findChildren(recursive=False)
        cols = [ele.get_text().strip() for ele in cols]
        print("Available Sizes:\n\t",cols)


    #---------------Other Categories--------------------
    other_categories_div = soup_level2.find('div', {'class': 'product__categories'})
    other_categories = ''
    for link in other_categories_div.find_all('a'):
        other_categories = other_categories + link.get_text().replace('\n', '') + ','
    print("Other Categories:\n\t", other_categories)

    #driver.execute_script("window.history.go(-1)")
    #count+=1
    break

print(count)
print("Done")
