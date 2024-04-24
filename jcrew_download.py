# Imports
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from urllib.request import urlopen
import cv2
import numpy as np


# Setup selenium
opts = ChromeOptions()
opts.add_argument("--window-size=1920,1080")
opts.add_argument("--headless")
opts.page_load_strategy = 'eager'
# opts.binary_location = "C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe"

# CONFIGURATIONS
# # Men's pants
# page = "https://www.jcrew.com/plp/mens/categories/clothing/pants-and-chinos?Npge=%d&Nrpp=120"
# num_pages = 2
# name = "jcrew_mens_pants"
# full_body = "d1"

# # Men's shirts
# page = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?Npge=%d&Nrpp=120"
# num_pages = 3
# name = "jcrew_mens_shirt"
# full_body = "m"

# # Men's sweaters
# page = "https://www.jcrew.com/plp/mens/categories/clothing/sweaters?Npge=%d&Nrpp=120"
# num_pages = 2
# name = "jcrew_mens_sweater"
# full_body = "m"

# # Men's shorts
# page = "https://www.jcrew.com/plp/mens/categories/clothing/shorts?Npge=%d&Nrpp=120"
# num_pages = 1
# name = "jcrew_mens_short"
# full_body = "d1"

# # Women's tops
# page = "https://www.jcrew.com/plp/womens/categories/clothing/shirts-and-tops?Npge=%d&Nrpp=120"
# num_pages = 2
# name = "jcrew_womens_tops"
# full_body = "m"

# # Women's pants
# page = "https://www.jcrew.com/plp/womens/categories/clothing/pants?Npge=%d&Nrpp=120"
# num_pages = 1
# name = "jcrew_womens_pants"
# full_body = "m"

# # Women's shorts
# page = "https://www.jcrew.com/plp/womens/categories/clothing/shorts?Npge=%d&Nrpp=120"
# num_pages = 1
# name = "jcrew_womens_shorts"
# full_body = "m"

# # Women's sweaters
# page = "https://www.jcrew.com/plp/womens/categories/clothing/sweaters?Npge=%d&Nrpp=120"
# num_pages = 2
# name = "jcrew_womens_sweaters"
# full_body = "m"

# Women's skirts
page = "https://www.jcrew.com/plp/womens/categories/clothing/skirts?Npg=%d"
num_pages = 1
name = "jcrew_womens_skirts"
full_body = "m"


for page_num in range(num_pages):
	driver = Chrome(options=opts)
	driver.delete_all_cookies()
	driver.get(page % (page_num + 1))

	# Get all product information
	product_tiles = driver.find_elements(By.CLASS_NAME, "product-tile")
	# product_tiles = [tile.find_element(By.CLASS_NAME, "product-tile--info") for tile in product_tiles]
	product_codes = [tile.find_element(By.TAG_NAME, "a").get_attribute("href").split("=")[4] for tile in product_tiles]
	print(product_codes)

	color_codes = [tile.find_elements(By.CLASS_NAME, "js-product__color") for tile in product_tiles]
	color_codes = [[color_code.get_attribute("data-code") for color_code in tile] for tile in color_codes]
	print(color_codes)

	# Close driver
	driver.close()

	# This image doesn't exist
	placeholder_img = urlopen("https://www.jcrew.com/s7-img-facade/BW595_WZ3976_d1").read()
	placeholder_img = cv2.imdecode(np.asarray(bytearray(placeholder_img), dtype=np.uint8), cv2.IMREAD_COLOR)

	# Some colors probably don't work more than others and no duplicates
	color_failures = {}
	downloaded_combinations = []

	# Download all images
	for i, (product, colors) in enumerate(zip(product_codes, color_codes)):
		if len(colors) < 1:
			continue

		for color in colors:
			if color_failures.get(color, 0) > 3 or (product, color) in downloaded_combinations:
				continue

			img_fb = urlopen("https://www.jcrew.com/s7-img-facade/%s_%s_%s" % (product, color, full_body)).read()
			img_fb = cv2.imdecode(np.asarray(bytearray(img_fb), dtype=np.uint8), cv2.IMREAD_COLOR)
			if np.sum(np.abs(img_fb - placeholder_img)) < 1: # Check if this is the same as jcrew's placeholder img
				color_failures[color] = color_failures.get(color, 0) + 1
				continue

			img_c = urlopen("https://www.jcrew.com/s7-img-facade/%s_%s" % (product, color)).read()
			img_c = cv2.imdecode(np.asarray(bytearray(img_c), dtype=np.uint8), cv2.IMREAD_COLOR)
			if np.sum(np.abs(img_fb - placeholder_img)) < 1: # Check if this is the same as jcrew's placeholder img
				color_failures[color] = color_failures.get(color, 0) + 1
				continue

			cv2.imwrite("data/%s-%s-%s-fb.png" % (name, product, color), img_fb)
			cv2.imwrite("data/%s-%s-%s-c.png" % (name, product, color), img_c)
			downloaded_combinations.append((product, color))
