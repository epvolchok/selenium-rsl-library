from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import json

class SeleniumExtractor():

    def __init__(self, isbn, headless=False):
        """
        Get ISBN and initilize webdriver
        """
        self.url = 'https://search.rsl.ru/ru/search#q='
        self.isbn = isbn

        self.options = webdriver.FirefoxOptions()
        if headless:
            self.options.add_argument('--headless')
        self.browser = webdriver.Firefox(options=self.options) # executable_path="./geckodriver"

    def __del__(self):
        """
        Close the browser
        """
        self.browser.quit()

    def get_data(self,):

        self.search()
        if self.num_results() > 0:

            self.open_desciptrion()

            self.search_marc()

            marc_table = self.extract_marc()

            table_data = self.get_table(marc_table)
        else:
            print('There is no results in this library')
            table_data = None

        return table_data
    
    def open_desciptrion(self):
        # Wait for the results to load
        self.wait(By.CLASS_NAME, 'js-item-maininfo')

        # Find and expand description
        search_dict = {
            'by': [By.TAG_NAME, By.CLASS_NAME],
            'element': ['a', 'rsl-itemaction-link']
        }
        description = self.find_element(depth=2, search_dict=search_dict)
        description.click()

    def search_marc(self):
        # Wait for the results to load
        css_sel = "#resultModal .modal-dialog .modal-content .modal-body #w0"
        self.wait(By.CSS_SELECTOR, css_sel)

        # Searching for marc-info
        find_marc = self.find_element(depth=1, search_dict={'by':[By.CSS_SELECTOR], 'element': [css_sel]})
        print(find_marc)
        last_item = find_marc.find_elements(By.TAG_NAME, "li")[-1]
        link = last_item.find_element(By.TAG_NAME, "a")
        link.click()

    def extract_marc(self):
        # Extract the info
        css_sel = "#resultModal .modal-dialog .modal-content .modal-body .tab-content #tab_marc"
        self.wait(By.CSS_SELECTOR, css_sel)

        search_dict = {
            'by': [By.CLASS_NAME, By.CSS_SELECTOR],
            'element': ['expanded_search', css_sel]
        }
        marc_table = self.find_element(depth=2, search_dict=search_dict)

        return marc_table

    def wait(self, by, element):
        """
        Wait until {element} load
        """
        element_wait = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((by, element)))

    def search(self):
        self.browser.get('https://search.rsl.ru/ru/search#q='+self.isbn)
        self.wait(By.CLASS_NAME, 'rsl-search-info')

    def num_results(self):
        """
        Number of search results
        """
        res = self.browser.find_element(By.CLASS_NAME, 'rsl-search-info')
        # position where the number of search results starts
        pattern = r':\s+'
        ind = re.search(pattern, res.text).end() + 1
        pattern = r'\d\d?'
        num = re.search(pattern, res.text[ind:])
        
        return int(num[0])
    
    def find_element(self, depth, search_dict):
        # Sequential search of several elements
        from_tosearch = self.browser
        while depth > 0:
            from_tosearch = from_tosearch.find_element(search_dict['by'][depth-1], search_dict['element'][depth-1])
            depth -= 1
        return from_tosearch
    
    def get_table(self, table_element):
        #Extracting data from table to a dict
        table_data = {}
        # Iterate over the rows of the table
        rows = table_element.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            # Initialize an empty list to store the cell data for this row
            row_data = []
            # Get all the cells in the current row
            cells = row.find_elements(By.TAG_NAME, "td")
            for cell in cells:
                # Extract text from the cell
                cell_text = cell.text
                # Add the cell text to the row data list
                row_data.append(cell_text)
            # Add the row data list to the table data dictionary
            table_data[row_data[0]] = row_data[1:]

        return table_data
    
    def dump_data(self, path, data):
        #Writing data to a file
        with open(path+'/data_'+self.isbn+'.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    

        
