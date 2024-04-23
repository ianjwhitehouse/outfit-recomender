# Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve


# Setup selenium
browser = webdriver.Chrome()
driver.implicitly_wait(5)

# Pants page 1
page = "https://www.jcrew.com/plp/mens/categories/clothing/pants-and-chinos?Npge=1&Nrpp=120"
name = "jcrew_pants_1"
# Pants page 2
# page = "https://www.jcrew.com/plp/mens/categories/clothing/pants-and-chinos?Npge=2&Nrpp=120"
# name = "jcrew_pants_2"

browser.get(page)

# Get all product buttons
product_tiles = driver.find_elements(By.CLASS_NAME, "product-tile")
product_tiles = [tile.find_element(By.CLASS_NAME, "product-tile--info") for tile in product_tiles]
buttons = [tile.find_element(By.TAG_NAME, "button") for tile in product_tiles]

# Click on all buttons and download images
# On J-crew, in the preview, the second image is always full-body and the fourth is always just clothes
for i, button in enumerate(buttons):
	button.click()
	quick_shop_panel = driver.find_element(By.ID, "c-quickshop__body")
	quick_shop_panel = quick_shop_panel.find_element(By.ID, "c-product__photos")
	imgs = quick_shop_panel.find_elements(By.TAG_NAME, "img")
	imgs = [img.get_attribute("src").split("?")[0] for img in imgs]
	urlretrieve(imgs[2], filename="imgs/%s_%d_fb.webp" % (name, i)) # Fb for full body
	urlretrieve(imgs[2], filename="imgs/%s_%d_jc.webp" % (name, i)) # Jc for just clothes