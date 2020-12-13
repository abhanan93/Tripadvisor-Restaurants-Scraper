from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime
import undetected_chromedriver as uc
import json
import time
import re
import xlsxwriter
import os, os.path
from restaurant import RestaurantScraper
from urlextractor import UrlExtractor

chromeOptions = uc.ChromeOptions()
chromeOptions.add_argument('--headless')
driver = uc.Chrome(options=chromeOptions)
country = input("Enter country: ")
restaurant = input("Enter restaurant: ")
print("[INFO] Starting scraper...")
urlExtractor = UrlExtractor(driver, country, restaurant)
urls = urlExtractor.run()
if os.path.isdir("Results") == False:
  os.mkdir("Results")

os.chdir("./Results")

timestamp = datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
xlsxWriter = xlsxwriter.Workbook('{}_{}_{}.xlsx'.format(country, restaurant, timestamp))
reviews = xlsxWriter.add_worksheet('Reviews')
summary = xlsxWriter.add_worksheet('Summary')
images = xlsxWriter.add_worksheet('Images')

reviewsCol = 0
reviewsRow = 0
summaryCol = 0
summaryRow = 0
imagesCol = 0
imagesRow = 0

merge_format = xlsxWriter.add_format({
    'bold': 1,
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': 'yellow'})
summary.merge_range('M1:P1', 'Ratings', merge_format)

merge_format = xlsxWriter.add_format({
    'bold': 1,
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': 'green'
})
summary.merge_range('Q1:U1', 'Reviews', merge_format)

headerFormat = xlsxWriter.add_format({
    'bold': 1,
    'align': 'center',
    'valign': 'vcenter',
})

summaryRow = 1
headers = ['Source', 'Country', 'City', 'Restaurant', 'Address',
            'Price', 'Cuisine1', 'Cuisine2', 'Cuisine3', 'Cuisine4',
            'Overall Rating', 'Total Reviews', 'Food', 'Service', 
            'Value', 'Atmosphere', 'Excellent', 'Very good', 'Average', 'Poor', 'Terrible']
for i, header in enumerate(headers):
  summary.write(summaryRow, summaryCol + i, header, headerFormat)
summaryRow += 1

headers = ['Source', 'Country', 'City', 'Restaurant',
            'Address', 'Image Sequence', 'Image URL']
for i, header in enumerate(headers):
  images.write(imagesRow, imagesCol + i, header, headerFormat)
imagesRow += 1

headers = ['Source', 'Country', 'City', 'Restaurant', 'Address', 
            'Name of Reviewer', 'From', 'Contributions', 'Helpful Votes',
            'Date of visit', 'Rating', 'Review Title', 'Review Body',
            'Review Response', 'Review URL']
for i, header in enumerate(headers):
  reviews.write(reviewsRow, reviewsCol + i, header, headerFormat)
reviewsRow += 1

color = '#a8ffc5'
#f7ffc2
cellFormat = xlsxWriter.add_format({
  'fg_color': color
})


if urls != False:
  for url in urls:
    print('[GET] {}'.format(url))
    try:
      restaurantScraper = RestaurantScraper(driver, url)
      restaurantData = restaurantScraper.run()
      summary.write(summaryRow, summaryCol, 'Tripadvisor', cellFormat)
      summary.write(summaryRow, summaryCol +   1, country, cellFormat)
      summary.write(summaryRow, summaryCol +   2, restaurantData['city'], cellFormat)
      summary.write(summaryRow, summaryCol +   3, restaurantData['restaurantTitle'], cellFormat)
      summary.write(summaryRow, summaryCol +   4, restaurantData['address'], cellFormat)
      summary.write(summaryRow, summaryCol +   5, restaurantData['price'], cellFormat)
      summary.write(summaryRow, summaryCol +   6, restaurantData['cuisine1'], cellFormat)
      summary.write(summaryRow, summaryCol +   7, restaurantData['cuisine2'], cellFormat)
      summary.write(summaryRow, summaryCol +   8, restaurantData['cuisine3'], cellFormat)
      summary.write(summaryRow, summaryCol +   9, restaurantData['cuisine4'], cellFormat)
      summary.write(summaryRow, summaryCol +  10, restaurantData['overallRating'], cellFormat)
      summary.write(summaryRow, summaryCol +  11, restaurantData['totalReviews'], cellFormat)
      summary.write(summaryRow, summaryCol +  12, restaurantData['food'], cellFormat)
      summary.write(summaryRow, summaryCol +  13, restaurantData['service'], cellFormat)
      summary.write(summaryRow, summaryCol +  14, restaurantData['value'], cellFormat)
      summary.write(summaryRow, summaryCol +  15, restaurantData['atmosphere'], cellFormat)
      summary.write(summaryRow, summaryCol +  16, restaurantData['excellentReviews'], cellFormat)
      summary.write(summaryRow, summaryCol +  17, restaurantData['vgoodReviews'], cellFormat)
      summary.write(summaryRow, summaryCol +  18, restaurantData['avgReviews'], cellFormat)
      summary.write(summaryRow, summaryCol +  19, restaurantData['poorReviews'], cellFormat)
      summary.write(summaryRow, summaryCol +  20, restaurantData['terribleReviews'], cellFormat)
      summaryRow += 1

      for imgSeq, imgUrl in restaurantData['imageUrls'].items():
        images.write(imagesRow, imagesCol +   0, 'Trip advisor', cellFormat)
        images.write(imagesRow, imagesCol +   1, country, cellFormat)
        images.write(imagesRow, imagesCol +   2, restaurantData['city'], cellFormat)
        images.write(imagesRow, imagesCol +   3, restaurantData['restaurantTitle'], cellFormat)
        images.write(imagesRow, imagesCol +   4, restaurantData['address'], cellFormat)
        images.write(imagesRow, imagesCol +   5, imgSeq, cellFormat)
        images.write(imagesRow, imagesCol +   6, imgUrl, cellFormat)
        imagesRow += 1

      for i in restaurantData['reviews']:
        reviews.write(reviewsRow, reviewsCol +   0, 'Trip advisor', cellFormat)
        reviews.write(reviewsRow, reviewsCol +   1, country, cellFormat)
        reviews.write(reviewsRow, reviewsCol +   2, restaurantData['city'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +   3, restaurantData['restaurantTitle'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +   4, restaurantData['address'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +   5, restaurantData['reviews'][i]['name'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +   6, restaurantData['reviews'][i]['location'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +   7, restaurantData['reviews'][i]['contributions'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +   8, restaurantData['reviews'][i]['votes'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +   9, restaurantData['reviews'][i]['visitDate'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +  10, restaurantData['reviews'][i]['rating'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +  11, restaurantData['reviews'][i]['reviewTitle'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +  12, restaurantData['reviews'][i]['reviewBody'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +  13, restaurantData['reviews'][i]['reviewResponse'], cellFormat)
        reviews.write(reviewsRow, reviewsCol +  14, restaurantData['reviews'][i]['reviewUrl'], cellFormat)
        reviewsRow += 1

      if color == '#a8ffc5':
        color = '#f7ffc2'
        cellFormat = xlsxWriter.add_format({
          'fg_color': color
        })
      else:
        color = '#a8ffc5'
        cellFormat = xlsxWriter.add_format({
          'fg_color': color
        })

    except Exception as e:
      print(e)
      xlsxWriter.close()
      break

print('[INFO] Saving results')
xlsxWriter.close()
driver.quit()
