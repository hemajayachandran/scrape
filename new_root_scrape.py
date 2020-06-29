from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
import time
from openpyxl.workbook import Workbook
from selenium.webdriver.chrome.options import Options

def create_session(url):
    try:
        driver = webdriver.Chrome(r'C:\Users\hemaa\Downloads\chromedriver_win32 (1)\chromedriver.exe')
        driver.implicitly_wait(30)
        driver.get(url)
        return driver
    except Exception as e:
        print("Exception occured while creating chrome session")

def load_page(driver):
    while True:
        try:
            loadmore = driver.find_element_by_id("loadMoreProducts")
            loadmore.click()
            time.sleep(5)
        except:
            print("Reached bottom of page")
            break
    return driver

def beautifulsoup(driver):
    try:
        soup_level = BeautifulSoup(driver.page_source, 'html.parser')
        return soup_level
    except Exception as e:
        print("Exception occured while beautifulsoup creation")

def fetch_product_links(soup_level):
    try:
        link_loaded = []
        for product_link in soup_level.find_all('a', {'class': "product-list__item__link"}):
            link_loaded.append(product_link.get('href'))
        print(len(link_loaded))
        return link_loaded
    except Exception as e:
        print("Exception occured while fetching product links")

def open_product_link(driver, link):
    try:
        actions = ActionChains(driver)
        python_button = driver.find_element_by_xpath("//a[@href="+"'"+link+"'"+"]")
        actions.key_down(Keys.CONTROL).click(python_button).key_up(Keys.CONTROL).perform()

        time.sleep(5)
        #window_after = driver.window_handles[1]
        driver.switch_to.window(driver.window_handles[1])
        return driver
    except Exception as e:
        print("Exception occured while opening product link")

def get_product_id(link):
    try:
        return link.split('/')[-1].replace("'", "")
    except Exception as e:
        print("Exception occured while fetching prodc")


def get_product_name(soup_level):
    try:
        product_name = soup_level.find('h1', {'class': 'product__name'})
        return product_name.get_text()
    except Exception as e:
        print("Exception occured while fetching product name")

def get_product_summary(soup_level):
    try:
        product_summary = soup_level.find('div', {'class': 'product__properties__size'})
        return product_summary.get_text()
    except Exception as e:
        print("Exception occured while fetching product summary")

def get_npn(soup_level):
    try:
        npn = soup_level.find('div', {'class': 'product__properties__npn'})
        if npn is not None:
            npn_value = npn.get_text()[5:]
        else:
            npn_value = None
        return npn_value
    except Exception as e:
        print("Exception occured while fetching npn")

def get_short_description(soup_level):
    try:
        short_descr_div = soup_level.find('div', {'class': 'product__description__short'})
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
        return short_description
    except Exception as e:
        print("Exception occured while fetching short description")

def get_long_description(soup_level):
    try:
        full_descr_div = soup_level.find('div', {'class': 'product__description__full'})
        full_description = ''
        for p in full_descr_div.find_all('p'):
            full_description += p.get_text()
        return full_description
    except Exception as e:
        print("Exception occured while fetching long description")

def get_directions_of_use(soup_level):
    try:
        directions_of_use_div = soup_level.find('div', {'class': 'product__use'})
        directions_of_use = ''
        for p in directions_of_use_div.find_all('p'):
            directions_of_use += p.get_text()
        return directions_of_use
    except Exception as e:
        print("Exception occured while fetching directions of use")

def other_categories(soup_level):
    try:
        navbar = soup_level.find('div', {'class': 'navbar__container'})
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
        other_categories_div = soup_level.find('div', {'class': 'product__categories'})
        product_features = {'Category': [], 'Gender / Life\xa0Stage': [], 'Health Benefits': []}
        for link in other_categories_div.find_all('a'):
            if link.get_text().replace('\n', '') in category_types['Category']:
                product_features['Category'].append(link.get_text().replace('\n', ''))
            elif link.get_text().replace('\n', '') in category_types['Gender / Life\xa0Stage']:
                product_features['Gender / Life\xa0Stage'].append(link.get_text().replace('\n', ''))
            elif link.get_text().replace('\n', '') in category_types['Health Benefits']:
                product_features['Health Benefits'].append(link.get_text().replace('\n', ''))
        return (','.join(product_features['Category']), ','.join(product_features['Gender / Life\xa0Stage']),','.join(product_features['Health Benefits']))
    except Exception as e:
        print("Exception occured while fetching categories")

def get_ingredients(soup_level, ingredients_df, product_id):
    try:
        temp_df = pd.DataFrame()
        ingredients_div = soup_level.find('div', {'class': 'product__ingredients'})
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
            return ingredient_text_list, pd.DataFrame()
        elif ingredients_table:
            for tr in ingredients_table.tbody.find_all('tr'):
                for td in tr.find_all('td'):
                    ingredient_text += td.get_text()
                    end = ingredient_text[-1]
                    if end not in ['.', ':']:
                        if td.get_text().count('Capsules') <=0:
                            ingredients_text_list.append(td.get_text())
                #print(ingredient_text_list)
                if len(ingredients_text_list) > 0:
                    if ''.join(ingredients_text_list[:len(ingredients_text_list)-1]).count('mg') > 0 or ''.join(ingredients_text_list[:len(ingredients_text_list)-1]).count('mcg') > 0 or ''.join(ingredients_text_list[:len(ingredients_text_list)-1]).count('IU') > 0:
                        ingredients.append(ingredients_text_list[0])
                        concentration = ','.join(ingredients_text_list[1:])
                    else:
                        ingredients.append(''.join(ingredients_text_list[:len(ingredients_text_list)-1]))
                        concentration = ingredients_text_list[-1:]

                    number_of_ingredients += 1
                    ingredient_column = 'Ingredient'+str(number_of_ingredients)
                    concentration_column = 'Concentration'+str(number_of_ingredients)

                    temp_df['PID'] = pd.Series(product_id,  dtype='object')
                    temp_df[ingredient_column] = pd.Series(ingredients,  dtype='object')
                    temp_df[concentration_column] = pd.Series(concentration, dtype='object')
                    #print(temp_df)
                    ingredients_text_list = []

                    ingredients = []
                    concentration = []
                ingredient_text_list.append(ingredient_text)
                ingredient_text = ''

            ingredients_df = ingredients_df.append(temp_df.tail(1))
            return ingredient_text_list, ingredients_df
    except Exception as e:
        print("Exception occured while processing ingredients")

def get_available_sizes(soup_level, product_id):
    try:
        available_sizes_df = pd.DataFrame(columns = ['PID', 'Format', 'Size', 'Code'])
        size_tab = soup_level.find('div', {'class': 'tab'})

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
        available_sizes_df = available_sizes_df.append(temp_df)
        return available_sizes_df
    except Exception as e:
        print("Exception occured while fetching available sizes {0}".str(e))

def get_related_products(soup_level):
    try:
        rel_pdt_div = soup_level.find('div', {'class': 'product__related'})
        related_products = []
        for pdt in rel_pdt_div.find_all('div', {'class': 'product__related__item__title'}):
            related_products.append(pdt.get_text())
        return ','.join(related_products)
    except Exception as e:
        print("Exception occured while fetching related products")

def process_products(driver, soup_level):
    try:
        products_df = pd.DataFrame(columns=['PID','Product Name', 'Summary', 'NPN', 'Short Description', 'Full Description', 'Directions of use', 'Related Products', 'Category', 'Gender/Life Stage',
                            'Health Benefits', 'Ingredients Used'])

        ingredients_df = pd.DataFrame()
        final_df = pd.DataFrame()
        found_links = []
        link_loaded = fetch_product_links(soup_level)

        count = 0
        #new_links = link_loaded[155:]
        for link in link_loaded:
            count += 1
            print(link)
            found_links.append(link)

            second_driver = open_product_link(driver, link)

            product_id = get_product_id(link)
            print(product_id)

            soup_level2 = beautifulsoup(second_driver)

            product_name = get_product_name(soup_level2)
            print(product_name)

            product_summary = get_product_summary(soup_level2)
            #print(product_summary)

            npn = get_npn(soup_level2)
            #print(npn)

            short_description = get_short_description(soup_level2)
            #print(short_description)
            long_description = get_long_description(soup_level2)
            #print(long_description)
            directions_of_use = get_directions_of_use(soup_level2)
            #print(directions_of_use)
            related_products = get_related_products(soup_level2)
            #print(related_products)
            category, gender_life_stage, health_benefits = other_categories(soup_level2)
            #print(category)
            #print(gender_life_stage)
            available_sizes_df = get_available_sizes(soup_level2, product_id)
            #print(available_sizes_df.head())
            ingredient_as_text, ingredients_df = get_ingredients(soup_level2, pd.DataFrame(), product_id)
            #print(ingredient_as_text)
            #print(ingredients_df.head())

            products_df = products_df.append({'PID': product_id,
                                              'Product Name': product_name,
                                              'Summary': product_summary,
                                              'NPN': npn,
                                              'Short Description': short_description,
                                              'Full Description': long_description,
                                              'Directions of use': directions_of_use,
                                              'Related Products': related_products,
                                              'Category': category,
                                              'Gender/Life Stage': gender_life_stage,
                                              'Health Benefits': health_benefits,
                                              'Ingredients Used': ''.join(ingredient_as_text)}, ignore_index=True)
            #print(products_df)
            if ingredients_df.empty == False:
                #print("******Inside*******")
                merge_ingredients_products = pd.merge(products_df, ingredients_df, on='PID')
                merge_products_available_sizes = pd.merge(merge_ingredients_products, available_sizes_df, on='PID')
            else:
                #print("Inside no ingr")
                merge_products_available_sizes = pd.merge(products_df, available_sizes_df, on='PID')

            final_df= final_df.append(merge_products_available_sizes)
            #print(final_df.head())
            print("Count:", count)
            time.sleep(10)
            second_driver.close()

            driver.switch_to.window(driver.window_handles[0])
        return final_df

    except Exception as e:
        print("Exception occured inside process_products")



if __name__ == "__main__":
    try:
        url = "https://newrootsherbal.ca/en/products/"

        driver = create_session(url)

        print("********Calling page load function**********")

        load_page(driver)

        soup_level = beautifulsoup(driver)
        output_df = process_products(driver, soup_level)
        output_df.to_excel('output_new.xlsx', index=False)
    except Exception as e:
        print("Exception occured")
