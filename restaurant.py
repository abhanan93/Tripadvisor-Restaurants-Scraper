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

class RestaurantScraper:
  def __init__(self, driver, url):
    self.driver = driver
    self.url = url
    self.pageHtml = None
    self.restaurantSchema = None
    self.itemsScraped = {
      'city': '',
      'address': '',
      'restaurantTitle': '',
      'price': '',
      'cuisine1': '',
      'cuisine2': '',
      'cuisine3': '',
      'cuisine4': '',
      'overallRating': '',
      'totalReviews': '',
      'food': '',
      'service': '',
      'value': '',
      'atmosphere': '',
      'excellentReviews': '',
      'vgoodReviews': '',
      'avgReviews': '',
      'poorReviews': '',
      'terribleReviews': '',
      'imageUrls': {},
      'reviews': {}
    }

  def scrape_schema(self, bs4Obj):
    try:
      restaurantSchema = bs4Obj.find('script', attrs={'type': 'application/ld+json'}).contents[0]
      self.restaurantSchema = json.loads(restaurantSchema)
    except Exception as e:
      # print(e)
      pass

  def scrape_city(self, bs4Obj):
    try:
      self.itemsScraped['city'] = self.restaurantSchema['address']['addressLocality']
    except Exception as e:
      # print(e)
      pass
  
  def scrape_address(self, bs4Obj):
    try:
      address = bs4Obj.find('a', attrs={'href': '#MAPVIEW'}).get_text()
      self.itemsScraped['address'] = address
    except Exception as e:
      # print(e)
      pass

  def scrape_price(self, bs4Obj):
    try:
      self.itemsScraped['price'] = self.restaurantSchema['priceRange']
    except Exception as e:
      # print(e)
      pass

  def scrape_cuisines(self, bs4Obj):
    try:
      relevantDivs = bs4Obj.find_all('div', attrs={'class': '_14zKtJkz'})
      cuisineDiv = None
      for div in relevantDivs:
        if div.find(text=re.compile('CUISINES')):
          cuisineDiv = div
          break

      if cuisineDiv != None:
        cuisines = cuisineDiv.find_next('div').get_text().split(',')
        for i, cuisine in enumerate(cuisines):
          cuisines[i] = cuisine.strip()
        if cuisines[0]:
          self.itemsScraped['cuisine1'] = cuisines[0]
        if cuisines[1]:
          self.itemsScraped['cuisine2'] = cuisines[1]
        if cuisines[2]:
          self.itemsScraped['cuisine3'] = cuisines[2]
        if cuisines[3]:
          self.itemsScraped['cuisine4'] = cuisines[3]
    except Exception as e:
      pass

  def scrape_overall_rating(self, bs4Obj):
    try:
      self.itemsScraped['overallRating'] = self.restaurantSchema['aggregateRating']['ratingValue']
    except Exception as e:
      # print(e)
      pass

  def scrape_total_reviews(self, bs4Obj):
    try:
      self.itemsScraped['totalReviews'] = self.restaurantSchema['aggregateRating']['reviewCount']
    except Exception as e:
      # print(e)
      pass

  def scrape_food_rating(self, bs4Obj):
    try:
      self.itemsScraped['food'] = self.get_bubble_rating(bs4Obj, 'Food')
    except Exception as e:
      # print(e)
      pass

  def scrape_service_rating(self, bs4Obj):
    try:
      self.itemsScraped['service'] = self.get_bubble_rating(bs4Obj, 'Service')
    except Exception as e:
      # print(e)
      pass

  def scrape_value_rating(self, bs4Obj):
    try:
      self.itemsScraped['value'] = self.get_bubble_rating(bs4Obj, 'Value')
    except Exception as e:
      # print(e)
      pass

  def scrape_atmosphere_rating(self, bs4Obj):
    try:
      self.itemsScraped['atmosphere'] = self.get_bubble_rating(bs4Obj, 'Atmosphere')
    except Exception as e:
      # print(e)
      pass

  def scrape_excellent_count(self, bs4Obj):
    try:
      self.itemsScraped['excellentReviews'] = self.get_count_per_rating_scale(bs4Obj, 'Excellent')
    except Exception as e:
      # print(e)
      pass

  def scrape_verygood_count(self, bs4Obj):
    try:
      self.itemsScraped['vgoodReviews'] = self.get_count_per_rating_scale(bs4Obj, 'Very good')
    except Exception as e:
      # print(e)
      pass

  def scrape_average_count(self, bs4Obj):
    try:
      self.itemsScraped['avgReviews'] = self.get_count_per_rating_scale(bs4Obj, 'Average')
    except Exception as e:
      # print(e)
      pass

  def scrape_poor_count(self, bs4Obj):
    try:
      self.itemsScraped['poorReviews'] = self.get_count_per_rating_scale(bs4Obj, 'Poor')
    except Exception as e:
      # print(e)
      pass

  def scrape_terrible_count(self, bs4Obj):
    try:
      self.itemsScraped['terribleReviews'] = self.get_count_per_rating_scale(bs4Obj, 'Terrible')
    except Exception as e:
      # print(e)
      pass

  def scrape_image_urls(self, bs4Obj):
    try:
      # //div[@data-prwidget-name='common_basic_image' and contains(@class, 'photo_widget')]/div/img[contains(@data-lazyurl, 'media')]
      imgIndice = bs4Obj.select("div[data-prwidget-name='common_basic_image'][class='photo_widget'] div img[data-lazyurl]")
      for i, div in enumerate(bs4Obj.find_all('div', attrs={
        'data-prwidget-name': 'common_basic_image',
        'class': 'photo_widget'
      })):
        self.itemsScraped['imageUrls'][str(i+1)] = div.find('div').find('img')['data-lazyurl']
    except Exception as e:
      # print(e)
      pass

  def scrape_title(self, bs4Obj):
    try:
      self.itemsScraped['restaurantTitle'] = bs4Obj.find('h1', attrs={'data-test-target':'top-info-header'}).get_text()
    except:
      pass

  def scrape_reviews(self, bs4Obj):
    try:
      reviewsContainer = bs4Obj.find('div', attrs={'id': 'REVIEWS'})
      i = len(self.itemsScraped['reviews']) + 1
      for review in reviewsContainer.find_all('div', attrs={'class': 'review-container'}):
        i = str(i)
        self.itemsScraped['reviews'][i] = {}
        try:
          self.itemsScraped['reviews'][i]['name'] = review.find('span', attrs={'class': 'scrname'}).get_text()
        except Exception as e:
          self.itemsScraped['reviews'][i]['name'] = ''
          pass

        try:
          self.itemsScraped['reviews'][i]['reviewTitle'] = review.find('span', class_='noQuotes').get_text()
        except Exception as e:
          self.itemsScraped['reviews'][i]['reviewTitle'] = ''
          pass

        try:
          badgeTexts = review.find_all('span', class_='badgetext')
          self.itemsScraped['reviews'][i]['contributions'] = badgeTexts[0].get_text()
          self.itemsScraped['reviews'][i]['votes'] = badgeTexts[0].get_text()
        except:
          self.itemsScraped['reviews'][i]['contributions'] = ''
          self.itemsScraped['reviews'][i]['votes'] = ''
          pass

        try:
          self.itemsScraped['reviews'][i]['location'] = review.find('span', attrs={'class': 'userLocation'}).get_text()
        except:
          self.itemsScraped['reviews'][i]['location'] = ''
          pass

        try:
          self.itemsScraped['reviews'][i]['visitDate'] = review.find('div', attrs={'data-prwidget-name': 'reviews_stay_date_hsx'}).contents[1].strip()
        except:
          self.itemsScraped['reviews'][i]['visitDate'] = ''
          pass

        try:
          self.itemsScraped['reviews'][i]['rating'] = str(int(review.find('span', attrs={'class': 'ui_bubble_rating'})['class'][1].replace('bubble_', ''))/10)
        except:
          self.itemsScraped['reviews'][i]['rating'] = ''
          pass

        try:
          self.itemsScraped['reviews'][i]['reviewBody'] = review.find('div', attrs={'data-prwidget-name': 'reviews_text_summary_hsx'}).get_text()
        except:
          self.itemsScraped['reviews'][i]['reviewBody'] = ''
          pass
        
        try:
          reviewUrl = review.find('div', class_='quote').find('a')['href']
          self.itemsScraped['reviews'][i]['reviewUrl'] = "https://tripadvisor.com" + reviewUrl
        except:
          self.itemsScraped['reviews'][i]['reviewUrl'] = ''
          pass

        try:
          reviewResponseDiv = review.find('div', attrs={'data-prwidget-name':'reviews_response_header'})
          self.itemsScraped['reviews'][i]['reviewResponse'] = reviewResponseDiv.find('p', class_='partial_entry').get_text()
        except:
          self.itemsScraped['reviews'][i]['reviewResponse'] = ''
          pass

        i = int(i) + 1

    except Exception as e:
      # print(e)
      pass


  def get_count_per_rating_scale(self, bs4Obj, scale):
    try:
      scaleTag = bs4Obj.find('label', text=re.compile('(.*){}(.*)'.format(scale)))
      count = scaleTag.find_next('span', attrs={'class': 'row_num'}).get_text()
      return count
    except Exception as e:
      # print(e)
      return ''

  def get_bubble_rating(self, bs4Obj, item):
    try:
      itemSpan = bs4Obj.find(text=item)
      itemRatingSpan = itemSpan.find_next('span').find('span')
      itemRatingSpanClass = itemRatingSpan['class'][1]
      rating = int(itemRatingSpanClass.replace('bubble_', ''))/10
      return str(rating)
    except Exception as e:
      # print(e)
      return ''

  def goto_reviews(self):
    try:
      self.driver.find_element_by_xpath("//div[@class='quote']/a").click()
    except Exception as e:
      # print(e)
      pass

  def click_next_reviews(self):
    try:
      self.driver.find_element_by_xpath("//div[contains(@class, 'ui_button') and contains(text(), 'Next')]").click()
    except Exception as e:
      # print(e)
      pass

  def next_reviews_disabled(self):
    try:
      nextBtn = self.driver.find_element_by_xpath("//div[contains(@class, 'ui_button') and contains(text(), 'Next')]")
      if 'disabled' in nextBtn.get_attribute('class'):
        return True
      else:
        return False
    except:
      return True

  def print_scraped(self):
    print(self.itemsScraped)

  def run(self):
    try:
      self.driver.get(self.url)
      element = WebDriverWait(self.driver, 20).until(
          EC.presence_of_element_located((By.XPATH, "//h1[@data-test-target='top-info-header']"))
      )
      bs4Obj = BeautifulSoup(self.driver.page_source, 'lxml')
      self.scrape_schema(bs4Obj)
      self.scrape_title(bs4Obj)
      self.scrape_city(bs4Obj)
      self.scrape_address(bs4Obj)
      self.scrape_price(bs4Obj)
      self.scrape_overall_rating(bs4Obj)
      self.scrape_total_reviews(bs4Obj)
      self.scrape_cuisines(bs4Obj)
      self.scrape_excellent_count(bs4Obj)
      self.scrape_verygood_count(bs4Obj)
      self.scrape_average_count(bs4Obj)
      self.scrape_poor_count(bs4Obj)
      self.scrape_terrible_count(bs4Obj)
      self.scrape_food_rating(bs4Obj)
      self.scrape_value_rating(bs4Obj)
      self.scrape_atmosphere_rating(bs4Obj)
      self.scrape_service_rating(bs4Obj)
      self.scrape_image_urls(bs4Obj)
      self.goto_reviews()
      element = WebDriverWait(self.driver, 20).until(
          EC.presence_of_element_located((By.XPATH, "//div[@id='taplc_location_reviews_list_sur_0']"))
      )
      bs4Obj = BeautifulSoup(self.driver.page_source, 'lxml')
      self.scrape_reviews(bs4Obj)
      oldDivState = bs4Obj.find('div', attrs={'id': 'taplc_location_reviews_list_sur_0'}).decode_contents()
      while self.next_reviews_disabled() == False:
        self.click_next_reviews()
        bs4Obj = BeautifulSoup(self.driver.page_source, 'lxml')
        while bs4Obj.find('div', attrs={'id': 'taplc_location_reviews_list_sur_0'}).decode_contents() == oldDivState:
          time.sleep(0.5)
          bs4Obj = BeautifulSoup(self.driver.page_source, 'lxml')
        self.scrape_reviews(bs4Obj)
        oldDivState = bs4Obj.find('div', attrs={'id': 'taplc_location_reviews_list_sur_0'}).decode_contents()
      #self.print_scraped()
      return self.itemsScraped
    except Exception as e:
      print("Failure occured in restaurant scraper. Possible cause of failure {}".format(e))
      return False

if __name__ == "__main__":
  driver = uc.Chrome()
  restaurantScraper = RestaurantScraper(driver, "https://www.tripadvisor.com/Restaurant_Review-g295424-d13994038-Reviews-Mirchi_Garden-Dubai_Emirate_of_Dubai.html")
  restaurantScraper.run()
  driver.quit()

  