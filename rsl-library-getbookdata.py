
from libselenium import SeleniumExtractor as sl
import os

def main(isbn):

    path = './Data'
    if not os.path.isdir(path):
        os.mkdir(path)

    # Initialize webdriver
    rsl = sl(isbn)
    data = rsl.get_data()
    if data:
        rsl.dump_data(path, data)

    return 0

if __name__ == '__main__':

    isbn_str = '9785000837801'
    main(isbn_str)
