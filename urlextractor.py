from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import json
import time
import re

class UrlExtractor:
  def __init__(self, driver, country, restaurant):
    self.driver = driver
    self.urlsScraped = []
    self.country = country
    self.restaurant = restaurant

  def select_country(self):
    try:
      inputField = self.driver.find_element_by_xpath("//input[@placeholder='Where to?']")
      inputField.click()
      inputField.send_keys(self.country)
      time.sleep(4)
      element = WebDriverWait(self.driver, 20).until(
          EC.presence_of_element_located((By.XPATH, "//div[@data-test-attribute='typeahead-results']//a"))
      )
      self.driver.find_element_by_xpath("//div[@data-test-attribute='typeahead-results']//a[1]").click()

    except Exception as e:
      # print(e)
      pass

  def click_restaurants(self):
    try:
      restaurantXpath = "//a[@data-tab-name='Restaurants']"
      element = WebDriverWait(self.driver, 20).until(
          EC.presence_of_element_located((By.XPATH, "//a[@data-tab-name='Restaurants']"))
      )
      self.driver.find_element_by_xpath(restaurantXpath).click()
    except Exception as e:
      # print(e)
      pass

  def select_restaurant(self):
    try:
      inputXpath = "//input[@type='search']"
      element = WebDriverWait(self.driver, 20).until(
          EC.presence_of_element_located((By.XPATH, "//a[@title='Restaurants']"))
      )
      time.sleep(2)
      self.driver.find_element_by_xpath(inputXpath).click()
      self.driver.find_element_by_xpath(inputXpath).send_keys(self.restaurant)
      self.driver.find_element_by_xpath(inputXpath).send_keys(Keys.ENTER)
    except Exception as e:
      # print(e)
      pass

  def wait_for_results(self):
    try:
      element = WebDriverWait(self.driver, 20).until(
          EC.presence_of_element_located((By.XPATH, "//div[@data-prwidget-name='search_search_result_poi']"))
      )
    except Exception as e:
      # print(e)
      pass

  def scrape_urls(self, bs4Obj):
    try:
      resultDivs = bs4Obj.find_all('div', attrs={'class': 'result-title'})
      for result in resultDivs:
        str = result['onclick']
        reg = re.compile("(.*)this, '(.*?)'(.*?)")
        url = "https://www.tripadvisor.com" + re.compile(reg).search(str).group(2)
        self.urlsScraped.append(url)
    except Exception as e:
      # print(e)
      pass

  def click_show_more(self):
    try:
      showMoreBtnXpath = "//span[contains(text(), 'Show more')]"
      element = WebDriverWait(self.driver, 20).until(
          EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Show more')]"))
      )
      showMoreBtn = self.driver.find_element_by_xpath(showMoreBtnXpath)
      showMoreBtn.click()
    except Exception as e:
      # print(e)
      pass

  def click_next(self):
    try:
      self.driver.find_element_by_xpath("//a[contains(@class, 'ui_button') and contains(text(), 'Next')]").click()
    except Exception as e:
      # print(e)
      pass

  def next_disabled(self):
    try:
      nextBtn = self.driver.find_element_by_xpath("//a[contains(@class, 'ui_button') and contains(text(), 'Next')]")
      if 'disabled' in nextBtn.get_attribute('class'):
        return True
      else:
        return False
    except:
      return False

  def print_scraped(self):
    for url in self.urlsScraped:
      print(url)


  def run(self):
    try:
      self.driver.get("https://www.tripadvisor.com")
      time.sleep(5)
      self.select_country()
      time.sleep(5)
      self.select_restaurant()
      self.click_restaurants()
      self.wait_for_results()
      bs4Obj = BeautifulSoup(self.driver.page_source, 'lxml')
      self.scrape_urls(bs4Obj)
      return self.urlsScraped
      oldDivState = bs4Obj.find('div', attrs={'class': 'search-results-list'}).decode_contents()
      while self.next_disabled() == False:
        self.click_next()
        self.wait_for_results()
        bs4Obj = BeautifulSoup(self.driver.page_source, 'lxml')
        while bs4Obj.find('div', attrs={'class': 'search-results-list'}).decode_contents() == oldDivState:
          time.sleep(0.5)
          bs4Obj = BeautifulSoup(self.driver.page_source, 'lxml')
        self.scrape_urls(bs4Obj)
        oldDivState = bs4Obj.find('div', attrs={'class': 'search-results-list'}).decode_contents()
      #self.print_scraped()
    except Exception as e:
      print("Failure occured in URL extraction. Possible cause of failure {}".format(e))
      return False
    return self.urlsScraped

if __name__ == "__main__":
  driver = uc.Chrome()
  urlExtractor = UrlExtractor(driver, "United Arab Emirates", "KFC")
  urlExtractor.run()
  driver.quit()
