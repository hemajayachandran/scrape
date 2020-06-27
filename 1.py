from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
import time
from openpyxl.workbook import Workbook

# Launch url
url = "https://newrootsherbal.ca/en/products/"

# Create a new chrome session (Chrome path has been given for Windows OS)
driver = webdriver.Chrome(r'C:\Users\hemaa\Downloads\chromedriver_win32 (1)\chromedriver.exe')
driver.implicitly_wait(30)
driver.get(url)

# Define pandas dataframe
df = pd.DataFrame(columns=['PID','Product Name', 'Summary', 'NPN', 'Short Description', 'Full Description', 'Directions of use', 'Related Products', 'Category', 'Gender/Life Stage',
                    'Health Benefits', 'Ingredients Used'])
df2 = pd.DataFrame(columns = ['PID', 'Format', 'Size', 'Code'])
df4 = pd.DataFrame()

# Define empty list to store already visited product links
links = []


while True:
    # While loop to load the page to get the entire products
    try:
        loadmore = driver.find_element_by_id("loadMoreProducts")
        loadmore.click()
        time.sleep(5)
    except:
        print("Reached bottom of page")
        break

# Selenium hands the page source to BeautifulSoup
soup_level1 = BeautifulSoup(driver.page_source, 'html.parser')

# Main page browser session
window_before = driver.window_handles[0]

# Empty list to store the product links
link_loaded = []

# BeautifulSoup finds all the product links and the loop begins
for link in soup_level1.find_all('a', {'class': "product-list__item__link"}):
    text = link.get('href').replace("'", "")
    if text not in links:
        link_loaded.append(link.get('href'))

# Loop will load each product and gets the data
for link in link_loaded:
    #count += 1
    links.append(link)

    product_id = link.split('/')[-1].replace("'", "")

    # To open the product link in a new tab
    actions = ActionChains(driver)
    python_button = driver.find_element_by_xpath("//a[@href="+"'"+link+"'"+"]")
    actions.key_down(Keys.CONTROL).click(python_button).key_up(Keys.CONTROL).perform()

    time.sleep(5)
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)


    # Selenium hands over the page source to next level
    soup_level2 = BeautifulSoup(driver.page_source, 'html.parser')


    # Finds the product name
    product_name = soup_level2.find('h1', {'class': 'product__name'})

    # Finds the product summary
    product_summary = soup_level2.find('div', {'class': 'product__properties__size'})

    # Finds NPN
    npn = soup_level2.find('div', {'class': 'product__properties__npn'})
    if npn is not None:
        npn_value = npn.get_text()[5:]
    else:
        npn_value = None



    #format = soup_level2.find('div', {'class': 'product__properties__format'})


    # Finds the product's short description
    short_descr_div = soup_level2.find('div', {'class': 'product__description__short'})
    list_of_p = short_descr_div.find_all('p')
    validated_list = []
    for item in list_of_p:
        updated = str(item).replace('<p>', '').replace('</p>', '')
        if updated != '' and '<!--' not in updated:
            validated_list.append(updated)

    if validated_list is not None:
        short_description = ''.join(validated_list)
    else:
        short_description = None

    # Finds the long description of the product
    full_descr_div = soup_level2.find('div', {'class': 'product__description__full'})
    full_description = ''
    for p in full_descr_div.find_all('p'):
        full_description += p.get_text()


    # Finds the directions of using the product
    directions_of_use_div = soup_level2.find('div', {'class': 'product__use'})
    directions_of_use = ''
    for p in directions_of_use_div.find_all('p'):
        directions_of_use += p.get_text()


    # Finds the ingredients
    df3 = pd.DataFrame()
    ingredients_div = soup_level2.find('div', {'class': 'product__ingredients'})
    ingredients_child_div = ingredients_div.find('div', {'class': 'product__ingredients__content'})
    ingredients_table = ingredients_child_div.find('table')

    ingredient_text = ''
    ingredient_text_list = []
    ingredients_text_list = []

    ingredients = []
    concentration = []
    number_of_ingredients = 0
    if ingredients_table is None:
        #-------------Processing ingredients not in table format----------------#
        ingredient_text += ingredients_child_div.get_text()
        ingredient_text_list.append(ingredient_text)
    elif ingredients_table:
        for tr in ingredients_table.tbody.find_all('tr'):
            for td in tr.find_all('td'):
                ingredient_text += td.get_text()
                end = ingredient_text[-1]
                if format != 'Powder':
                    if end not in ['.', ':']:
                        ingredients_text_list.append(td.get_text())
            if len(ingredients_text_list) > 0:
                ingredients.append(''.join(ingredients_text_list[:len(ingredients_text_list)-1]))
                concentration = ingredients_text_list[-1:]

                number_of_ingredients += 1
                ingredient_column = 'Ingredient'+str(number_of_ingredients)
                concentration_column = 'Concentration'+str(number_of_ingredients)

                df3['PID'] = pd.Series(product_id)
                df3[ingredient_column] = pd.Series(ingredients)
                df3[concentration_column] = pd.Series(concentration)

                ingredients_text_list = []

                ingredients = []
                concentration = []
            ingredient_text_list.append(ingredient_text)
            ingredient_text = ''
    df4 = df4.append(df3.tail(1))

    # Finds the related products list
    rel_pdt = soup_level2.find('div', {'class': 'product__related'})
    related_products = []
    for pdt in rel_pdt.find_all('div', {'class': 'product__related__item__title'}):
        related_products.append(pdt.get_text())


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
        category_types['Category'].append(item.get_text(strip=True).replace('\n', ''))
    for item in item_div[1].find_all('a'):
        category_types['Gender / Life\xa0Stage'].append(item.get_text(strip=True).replace('\n', ''))
    for item in item_div[2].find_all('a'):
        category_types['Health Benefits'].append(item.get_text(strip=True).replace('\n', ''))

    # Finds the product's categories
    other_categories_div = soup_level2.find('div', {'class': 'product__categories'})
    product_features = {'Category': [], 'Gender / Life\xa0Stage': [], 'Health Benefits': []}
    for link in other_categories_div.find_all('a'):
        if link.get_text().replace('\n', '') in category_types['Category']:
            product_features['Category'].append(link.get_text().replace('\n', ''))
        elif link.get_text().replace('\n', '') in category_types['Gender / Life\xa0Stage']:
            product_features['Gender / Life\xa0Stage'].append(link.get_text().replace('\n', ''))
        elif link.get_text().replace('\n', '') in category_types['Health Benefits']:
            product_features['Health Benefits'].append(link.get_text().replace('\n', ''))


    # Finds the available sizes of the product
    size_tab = soup_level2.find('div', {'class': 'tab'})

    # Empty lists
    size = []
    pid = []
    for tb_row in size_tab.find_all('div', {'class': 'tab__row'}):
        cols = tb_row.findChildren(recursive=False)
        col1 = [ele.get_text().replace('\n', '').strip() for ele in cols if ele.get_text().replace('\n', '').strip() not in ['Format', 'Size', 'Code']]
        if len(col1) > 0:
            size.append(col1)
            pid.append(product_id)
    for tb_row in size_tab.find_all('a', {'class': 'tab__row'}):
        cols = tb_row.findChildren(recursive=False)
        col1 = [ele.get_text().replace('\n', '').strip() for ele in cols if ele.get_text().replace('\n', '').strip() not in ['Format', 'Size', 'Code']]
        if len(col1) > 0:
            size.append(col1)
            pid.append(product_id)

    temp_df = pd.DataFrame(size, columns=['Format', 'Size', 'Code'])
    temp_df['PID'] = pid

    # Pandas dataframe will store the details of available sizes
    df2 = df2.append(temp_df)



    # Pandas dataframe stores all product related details
    df = df.append({'PID': product_id,
                    'Product Name': product_name.get_text(),
                    'Summary': product_summary.get_text(),
                    'NPN': npn_value,
                    'Short Description': short_description,
                    'Full Description': full_description,
                    'Directions of use': directions_of_use,
                    'Related Products': ','.join(related_products),
                    'Category': ','.join(product_features['Category']),
                    'Gender/Life Stage': ','.join(product_features['Gender / Life\xa0Stage']),
                    'Health Benefits': ','.join(product_features['Health Benefits']),
                    'Ingredients Used': ''.join(ingredient_text_list)}, ignore_index=True)

    # Close the current product page session and go back to main page
    driver.close()
    time.sleep(5)
    driver.switch_to.window(window_before)


# Merge main dataframe with ingredients dataframe
res1 = pd.merge(df, df4, on='PID')

# Merge above result with available sizes dataframe
res = pd.merge(res1, df2, on='PID')

# Load the final dataframe into an excel sheet.
res.to_excel('output.xlsx', index=False)
print("Done")
