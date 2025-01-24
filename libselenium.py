from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import json

class SeleniumExtractor():
    def __init__(self, isbn):
        """
        Get ISBN and initilize webdriver
        """
        self.url = 'https://search.rsl.ru/ru/search#q='
        self.isbn = isbn

        self.options = webdriver.FirefoxOptions()
        #options.add_argument("--headless")
        self.browser = webdriver.Firefox(options=self.options) # executable_path="./geckodriver"

    def __del__(self):
        """
        Close the browser
        """
        self.browser.quit()

    def wait(self, by, element):
        """
        Wait until {element} load
        """
        element_wait = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((by, element)))

    def search(self):
        self.browser.get("https://search.rsl.ru/ru/search#q="+self.isbn)
        self.wait(By.CLASS_NAME, 'rsl-search-info')

    def num_results(self):
        """
        Number of search results
        """
        res = self.browser.find_element(By.CLASS_NAME, "rsl-search-info")
        # position where the number of search results starts
        pattern = r':\s+'
        ind = re.search(pattern, res.text).end() + 1
        pattern = r'\d\d?'
        num = re.search(pattern, res.text[ind:])
        return num
    
    def get_data(self,):

        self.search()
        if self.num_results() > 0:
            self.wait(By.CLASS_NAME, 'js-item-maininfo')
            # Find and expand description
            elem = self.browser.find_element(By.CLASS_NAME, 'rsl-itemaction-link')
            desr = elem.find_element(By.TAG_NAME, 'a').click()

            # Wait for the results to load
            css_sel = "#resultModal .modal-dialog .modal-content .modal-body #w0"
            self.wait(By.CSS_SELECTOR, css_sel)
            

            # Searching for marc-info
            info = self.browser.find_element(By.CSS_SELECTOR, css_sel)
            list_ = info.find_elements(By.TAG_NAME, "li")
            last_item = list_[-1]

            link = last_item.find_element(By.TAG_NAME, "a")
            link.click()

        
