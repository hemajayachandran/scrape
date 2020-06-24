from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import sys
import time


#launch url
url = "https://newrootsherbal.ca/en/products/"

#create a new chrome session
driver = webdriver.Chrome(r'C:\Users\hemaa\Downloads\chromedriver_win32 (1)\chromedriver.exe')
driver.implicitly_wait(30)
driver.get(url)

"""while True:
    try:
        loadmore = driver.find_element_by_id("loadMoreProducts")
        loadmore.click()
        time.sleep(5)
    except Exception:
        print("Reached bottom of page")
        break"""
soup_level1 = BeautifulSoup(driver.page_source, 'html.parser')

"""for category in soup_level1.find_all('option'):
    print(category.get_text())"""

#BeautifulSoup grabs all products link specific to that category
count = 0
"""links = [link.get('href') for link in soup_level1.find_all('a', {'class': "product-list__item__link"})]
print(len(links))
print(links)

print(count)"""
with open('links.txt', 'r') as f:
    links = f.read()
link_list = links.split(',')
#print(link_list)
i=0
for link in link_list:
    print(link)
    python_button = driver.find_element_by_xpath("//a[@href="+link+"]")
    #driver.implicitly_wait(50)

    print("about to click")
    driver.execute_script("arguments[0].click();", python_button)
    time.sleep(20)
    print("Inside the product page")

    #driver.switch_to.window(driver.window_handles[1])#locate the first new page (handles)
    i+=1
    driver.switch_to.window(driver.window_handles[i])
    soup_level2 = BeautifulSoup(driver.page_source, 'html.parser')

    #-------------Product Name----------------
    product_name = soup_level2.find('h1', {'class': 'product__name'})
    print("Product Name: ", product_name.get_text())

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

    #-------------Related Products--------
    rel_pdt = soup_level2.find('div', {'class': 'product__related'})
    related_products = []
    for pdt in rel_pdt.find_all('div', {'class': 'product__related__item__title'}):
        related_products.append(pdt.get_text())
    print("Related Products: ",related_products)

    #driver.execute_script("window.history.go(-1)")
    back_button = driver.find_element_by_xpath("//a[@href='https://newrootsherbal.ca/en/products']")
    driver.execute_script("arguments[0].click();", back_button)
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[0])
print("Done")
