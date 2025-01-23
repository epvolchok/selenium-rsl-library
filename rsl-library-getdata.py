from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import json

# Initialize webdriver
options = webdriver.FirefoxOptions()
#options.add_argument("--headless")
browser = webdriver.Firefox(executable_path="./geckodriver", options=options)
isbn_str = "9785000837801"
browser.get("https://search.rsl.ru/ru/search#q="+isbn_str)

# Wait for the search results to load
element_wait = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rsl-search-info")))

# Are the results found
res = browser.find_element(By.CLASS_NAME, "rsl-search-info")
pattern = r":\s+"
ind = re.search(pattern, res.text).end()

table_data = {}

if (int(res.text[ind:ind+1]) > 0):
    #если больше 1, то будет разбирать просто первый нашедшийся результат
    element_wait = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "js-item-maininfo")))

    # Find and expand description
    elem = browser.find_element(By.CLASS_NAME, "rsl-itemfooter-link")
    desr = elem.find_element(By.TAG_NAME, "a").click()

    # Wait for the results to load
    css_sel = "#resultModal .modal-dialog .modal-content .modal-body #w0"
    element_wait = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_sel)))

    # Searching for marc-info
    info = browser.find_element(By.CSS_SELECTOR, css_sel)
    list_ = info.find_elements(By.TAG_NAME, "li")
    last_item = list_[-1]

    link = last_item.find_element(By.TAG_NAME, "a")
    link.click()

    # Extract the info
    css_sel = "#resultModal .modal-dialog .modal-content .modal-body .tab-content #tab_marc"
    element_wait = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_sel)))

    marc = browser.find_element(By.CSS_SELECTOR, css_sel)
    table = marc.find_element(By.CLASS_NAME, "expanded_search")
    

    # Iterate over the rows of the table
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row_index, row in enumerate(rows):
        # Initialize an empty list to store the cell data for this row
        row_data = []
        # Get all the cells in the current row
        cells = row.find_elements(By.TAG_NAME, "td")
        for cell_index, cell in enumerate(cells):
            # Extract text from the cell
            cell_text = cell.text
            # Add the cell text to the row data list
            row_data.append(cell_text)
        # Add the row data list to the table data dictionary
        table_data[row_data[0]] = row_data[1:]
    # Print the table data dictionary

    print(table_data)
    with open("data_"+isbn_str+".json", "w") as f:
        json.dump(table_data, f, indent=4, ensure_ascii=False)

elif (int(res.text[ind:ind+1]) == 0):
    # добавить запись в логи
    print("there is no results in this library")

# Close the browser window when done
# driver.quit()
