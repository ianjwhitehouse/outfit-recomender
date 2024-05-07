# Imports
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from urllib.request import urlopen
import cv2
import numpy as np
from time import sleep
from remove_bg_and_crop import rm_img_bg, get_img_crops, rm_img_bg_outside_range


# Setup selenium
opts = ChromeOptions()
opts.add_argument("--window-size=1920,1080")
opts.add_argument("--headless")
# opts.page_load_strategy = 'eager'
# opts.binary_location = "C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe"

# CONFIGURATIONS
pages = [
	("https://www.ae.com/us/en/c/men/tops/shirts/cat40005", "ae_mens_shirt"),
	("https://www.ae.com/us/en/c/men/tops/polos/cat510004", "ae_mens_shirt"),
	("https://www.ae.com/us/en/c/men/tops/graphic-tops/cat90018", "ae_mens_shirt"),
	("https://www.ae.com/us/en/c/men/bottoms/jeans/cat6430041", "ae_mens_pants"),
	("https://www.ae.com/us/en/c/men/bottoms/pants-/cat40003", "ae_mens_pants"),
	("https://www.ae.com/us/en/c/men/bottoms/joggers-sweatpants/cat7010052", "ae_mens_pants"),
	("https://www.ae.com/us/en/c/men/tops/jackets/cat380145", "ae_mens_sweater"),
	("https://www.ae.com/us/en/c/women/tops/tank-tops/cat380157", "ae_womens_tops"),
	("https://www.ae.com/us/en/c/women/tops/button-up-shirts/cat7670003", "ae_womens_tops"),
	("https://www.ae.com/us/en/c/women/tops/graphic-tees/cat90042", "ae_womens_tops"),
	("https://www.ae.com/us/en/c/women/tops/t-shirts/cat90030", "ae_womens_tops"),
	("https://www.ae.com/us/en/c/women/tops/sweaters-cardigans/cat1410002", "ae_womens_sweater"),
	("https://www.ae.com/us/en/c/women/tops/hoodies-sweatshirts/cat90048", "ae_womens_sweater"),
	("https://www.ae.com/us/en/c/women/bottoms/shorts/cat380159", "ae_womens_short"),
	("https://www.ae.com/us/en/c/women/bottoms/pants/cat90034", "ae_womens_pants"),
	("https://www.ae.com/us/en/c/women/bottoms/joggers-sweatpants/cat7010091", "ae_womens_pants"),
	("https://www.ae.com/us/en/c/women/bottoms/jeans/cat6430042", "ae_womens_pants"),
	("https://www.ae.com/us/en/c/women/bottoms/skirts-skorts/cat5920105", "ae_womens_skirts"),
]

# This image doesn't exist
placeholder_img = urlopen("https://s7d2.scene7.com/is/image/aeo/0152_6120_204_of?$pdp-m-opt$").read()
placeholder_img = cv2.imdecode(np.asarray(bytearray(placeholder_img), dtype=np.uint8), cv2.IMREAD_COLOR)
placeholder_img = cv2.resize(placeholder_img, (255, 255))

for page, name in pages:
	driver = Chrome(options=opts)
	driver.delete_all_cookies()
	driver.get(page)
	sleep(10)

	driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

	# Get all product information
	product_tiles = driver.find_elements(By.CLASS_NAME, "product-tile")
	product_codes = [tile.get_attribute("data-product-id") for tile in product_tiles]
	print(product_codes)

	# Close driver
	driver.close()

	# No duplicates
	downloaded_combinations = []

	for prod in product_codes:
		if prod in downloaded_combinations:
			continue
		downloaded_combinations.append(prod)

		# Download clothing on its own
		img_c = urlopen("https://s7d2.scene7.com/is/image/aeo/%s_f?$pdp-m-opt$" % prod).read()
		img_c = cv2.imdecode(np.asarray(bytearray(img_c), dtype=np.uint8), cv2.IMREAD_COLOR)
		if np.sum(np.abs(cv2.resize(img_c, (255, 255)) - placeholder_img)) < 16: # Check if this is the same as ae's placeholder img
			continue

		try:
			# Get the item color range
			img_c_no_bg = rm_img_bg(img_c)
			# cv2.imwrite("data/%s-%s-%s-fb.png" % (name, prod, "nb"), img_c_no_bg)
			img_c_no_bg = np.reshape(img_c_no_bg, (-1, 3))
			img_c_no_bg = img_c_no_bg[np.any(img_c_no_bg != 0, axis=-1)]
			color_range_min = np.percentile(img_c_no_bg, .1, axis=0)
			color_range_max = np.percentile(img_c_no_bg, .9, axis=0)
		except IndexError:
			continue

		# Download two angles just in case
		img_fb_1 = urlopen("https://s7d2.scene7.com/is/image/aeo/%s_of?$pdp-m-opt$" % prod).read()
		img_fb_1 = cv2.imdecode(np.asarray(bytearray(img_fb_1), dtype=np.uint8), cv2.IMREAD_COLOR)
		same_as_ph_1 = np.sum(np.abs(cv2.resize(img_fb_1, (255, 255)) - placeholder_img)) < 16

		img_fb_2 = urlopen("https://s7d2.scene7.com/is/image/aeo/%s_os?$pdp-m-opt$" % prod).read()
		img_fb_2 = cv2.imdecode(np.asarray(bytearray(img_fb_2), dtype=np.uint8), cv2.IMREAD_COLOR)
		same_as_ph_2 = np.sum(np.abs(cv2.resize(img_fb_2, (255, 255)) - placeholder_img)) < 16

		img_fb_3 = urlopen("https://s7d2.scene7.com/is/image/aeo/%s_ob?$pdp-m-opt$" % prod).read()
		img_fb_3 = cv2.imdecode(np.asarray(bytearray(img_fb_3), dtype=np.uint8), cv2.IMREAD_COLOR)
		same_as_ph_3 = np.sum(np.abs(cv2.resize(img_fb_3, (255, 255)) - placeholder_img)) < 16

		# Pick best image (first if only one exists, then the one with smaller horizontal/vertical
		if same_as_ph_1 and same_as_ph_2 and same_as_ph_3:
			continue
		else:
			print(color_range_max, color_range_min)
			imgs = [img_fb_1, img_fb_2, img_fb_3]
			same_as_ph = [same_as_ph_1, same_as_ph_2, same_as_ph_3]
			img_item_widths = [
				get_img_crops(
					rm_img_bg_outside_range(
						imgs[i],
						color_range_min,
						color_range_max,
					)
				) if not same_as_ph[i] else (np.inf, np.inf, np.inf, np.inf) for i in range(3)
			]
			img_item_widths = [
				(img_item_widths[i][3] - img_item_widths[i][1]) / imgs[i].shape[1] for i in range(3)
			]
			img_item_widths = [
				width if width > 0.25 else 1 for width in img_item_widths
			]

			print(img_item_widths)

			img_fb = imgs[np.argmin(img_item_widths)]

		cv2.imwrite("data/%s-%s-%s-fb.png" % (name, prod, "nc"), img_fb)
		cv2.imwrite("data/%s-%s-%s-c.png" % (name, prod, "nc"), img_c)
