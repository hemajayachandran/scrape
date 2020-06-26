from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import sys
import time
from openpyxl.workbook import Workbook
from selenium.common.exceptions import NoSuchElementException


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


#BeautifulSoup grabs all products link specific to that category
"""count = 0
links = [link.get('href') for link in soup_level1.find_all('a', {'class': "product-list__item__link"})]
print(len(links))"""
#print(links)

"""#print(count)
with open('links1.txt', 'w+') as f:
    for link in links:
        f.write(link)
#link_list = links.split(',')"""


with open('links.txt', 'r') as f:
    links = f.read()
link_list = links.split(',')


#print(link_list)
i=0
df = pd.DataFrame(columns=['PID','Product Name', 'Summary', 'NPN', 'Short Description', 'Full Description', 'Directions of use', 'Ingredients', 'Concentration', 'Related Products', 'Category', 'Gender/Life Stage',
                    'Health Benefits'])
df2 = pd.DataFrame(columns = ['PID', 'Format', 'Size', 'Code'])
new_list = link_list
count = 0
for link in new_list:
    print(link)
    product_id = link.split('/')[-1].replace("'", "")
    #string ='https://newrootsherbal.ca'
    #if string not in link:
    #    link = "'"+(string+link.replace("'", "")).replace(" ", "")+"'"
    python_button = driver.find_element_by_xpath("//a[@href="+link+"]")
    print(python_button)
    time.sleep(30)

    #python_button = driver.find_element_by_xpath("//a[@href="+"'/product/id/1428'"+"]")
    #driver.implicitly_wait(10)

    print("about to click")
    driver.execute_script("arguments[0].click();", python_button)
    time.sleep(10)
    print("Inside the product page")

    #driver.switch_to.window(driver.window_handles[1])#locate the first new page (handles)
    #i+=1
    driver.switch_to.window(driver.window_handles[1])
    soup_level2 = BeautifulSoup(driver.page_source, 'html.parser')


    #-------------Product Name----------------
    product_name = soup_level2.find('h1', {'class': 'product__name'})
    print("Product Name: ", product_name.get_text())

    #-------------Product Summary--------------
    product_summary = soup_level2.find('div', {'class': 'product__properties__size'})
    #print("Summary: ", product_summary.get_text())

    #-------------NPN-------------------------
    npn = soup_level2.find('div', {'class': 'product__properties__npn'})
    if npn is not None:
        #print("NPN: ", npn.get_text()[5:])
        npn_value = npn.get_text()[5:]
    else:
        npn_value = None


    #------------Format-----------------------
    format = soup_level2.find('div', {'class': 'product__properties__format'})
    #print("Format: ", format.get_text()[8:])

    #------------Short Description-------------
    short_descr_div = soup_level2.find('div', {'class': 'product__description__short'})
    list_of_p = short_descr_div.find_all('p')
    short_description = list_of_p[1]
    #print("Short Description:\n\t", short_description.get_text())

    #-------------Full Description-------------
    full_descr_div = soup_level2.find('div', {'class': 'product__description__full'})
    full_description = ''
    for p in full_descr_div.find_all('p'):
        full_description += p.get_text()
    #print("Full Description:\n\t ", full_description)

    #-------------Directions of use--------------
    directions_of_use_div = soup_level2.find('div', {'class': 'product__use'})
    directions_of_use = ''
    for p in directions_of_use_div.find_all('p'):
        directions_of_use += p.get_text()
    #print("Directions of use:\n\t ", directions_of_use)


    #-------------Ingredients------------
    ingr_table = soup_level2.find('table')
    ingr_used = []
    string = ''
    for tr in ingr_table.tbody.find_all('tr'):
        for td in tr.find_all('td'):
            string += td.get_text()
        ingr_used.append(string)
        string = ''
    #print("Ingredients used:\n\t", ingr_used)

    #-------------Related Products--------
    rel_pdt = soup_level2.find('div', {'class': 'product__related'})
    related_products = []
    for pdt in rel_pdt.find_all('div', {'class': 'product__related__item__title'}):
        related_products.append(pdt.get_text())
    #print("Related Products: ",related_products)

    #----------------Product Features----------------
    navbar = soup_level2.find('div', {'class': 'navbar__container'})
    pdt_dropdown = navbar.find_all('li')
    category_types = {}
    for drp_div in pdt_dropdown[0].find_all('div', {'class': 'category-types__item'}):
        category_types[(drp_div.get_text(strip=True).replace('\n', ''))] = []

    #---------------Product Dropdowns;Category, Gender/Life Stage, Health Benefits-----------------
    drp_item_div = pdt_dropdown[0].find('div', {'class': 'categories'})
    item_div = drp_item_div.find_all('div', {'class': 'categories__col'})
    for item in item_div[0].find_all('a'):
        #print(item_div[0])
        category_types['Category'].append(item.get_text(strip=True).replace('\n', ''))
    for item in item_div[1].find_all('a'):
        #print(item_div[0])
        category_types['Gender / Life\xa0Stage'].append(item.get_text(strip=True).replace('\n', ''))
    for item in item_div[2].find_all('a'):
        #print(item_div[0])
        category_types['Health Benefits'].append(item.get_text(strip=True).replace('\n', ''))

    #---------------Other Categories--------------------
    other_categories_div = soup_level2.find('div', {'class': 'product__categories'})
    product_features = {'Category': [], 'Gender / Life\xa0Stage': [], 'Health Benefits': []}
    for link in other_categories_div.find_all('a'):
        if link.get_text().replace('\n', '') in category_types['Category']:
            product_features['Category'].append(link.get_text().replace('\n', ''))
        elif link.get_text().replace('\n', '') in category_types['Gender / Life\xa0Stage']:
            product_features['Gender / Life\xa0Stage'].append(link.get_text().replace('\n', ''))
        elif link.get_text().replace('\n', '') in category_types['Health Benefits']:
            product_features['Health Benefits'].append(link.get_text().replace('\n', ''))


    #---------------Available Sizes--------------------
    #size_tab = soup_level2.find_all('div', {'class': 'tab'})
    size_tab = soup_level2.find('div', {'class': 'tab'})
    #dic = {'PID': [], 'Format': [], 'Size': [], 'Code': []}
    size = []
    pid = []
    for tb_row in size_tab.find_all('div', {'class': 'tab__row'}):
        cols = tb_row.findChildren(recursive=False)
        print(cols)
        col1 = [ele.get_text().replace('\n', '').strip() for ele in cols if ele.get_text().replace('\n', '').strip() not in ['Format', 'Size', 'Code']]
        if len(col1) > 0:
            size.append(col1)
            pid.append(product_id)
            print(size)
    for tb_row in size_tab.find_all('a', {'class': 'tab__row'}):
        cols = tb_row.findChildren(recursive=False)
        print(cols)
        col1 = [ele.get_text().replace('\n', '').strip() for ele in cols if ele.get_text().replace('\n', '').strip() not in ['Format', 'Size', 'Code']]
        if len(col1) > 0:
            size.append(col1)
            pid.append(product_id)
            print(size)

    temp_df = pd.DataFrame(size, columns=['Format', 'Size', 'Code'])
    temp_df['PID'] = pid

    #df2 = pd.concat([df2, temp_df])
    df2 = df2.append(temp_df)
        #print("Available Sizes:\n\t",cols)


    #-----------------Adding to dataframe---------
    df = df.append({'PID': product_id,
                    'Product Name': product_name.get_text(),
                    'Summary': product_summary.get_text(),
                    'NPN': npn_value,
                    'Short Description': short_description.get_text(),
                    'Full Description': full_description,
                    'Directions of use': directions_of_use,
                    'Ingredients': ','.join(ingr_used),
                    'Related Products': ','.join(related_products),
                    'Category': ','.join(product_features['Category']),
                    'Gender/Life Stage': ','.join(product_features['Gender / Life\xa0Stage']),
                    'Health Benefits': ','.join(product_features['Health Benefits'])}, ignore_index=True)
    print(df.head())
    print(df.shape)
    print(df2.head())

    count += 1
    if count == 3:
        break
    #driver.execute_script("window.history.go(-1)")
    driver2 = driver
    #back_button = driver.find_element_by_xpath("//a[@href='https://newrootsherbal.ca/en/products']")
    #driver.execute_script("arguments[0].click();", back_button)
    driver2.close()
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[0])
res = pd.merge(df, df2, on='PID')
print(res.head())
res.to_excel('output.xlsx', index=False)
print("Done")
