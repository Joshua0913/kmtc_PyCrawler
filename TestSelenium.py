import unittest

from selenium import webdriver

class TestSelenium(unittest.TestCase):
    def set_up(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://www.allegro.pl")
        self.search_text = "Laptop"
        self.search_field_id = "//input[@id='main-search-text']"
        self.search_button_id = "//input[@class='search-btn']"
        self.search_result_item_title = "//article[@class='offer offer-brand']//h2//span"

    def test_search_in_allegro_pl(self):
        driver = self.driver
        driver.find_element_by_xpath(self.search_field_id).send_keys(self.search_text)
        search_button = driver.find_element_by_xpath(self.search_button_id)
        search_button.submit()
        driver.implicitly_wait(5000)
        result = driver.find_elements_by_xpath(self.search_result_item_title).__getitem__(0).get_attribute("text")
        self.assertIn(self.search_text, result)

    def tear_down(self):
        self.driver.close()