# Imports
import cv2
import numpy as np

from os import listdir
from os.path import isfile, join


# Process all files in directory
only_files = [f for f in listdir("data/") if isfile(join("data/", f))]

for path in only_files:
	print(path)
	img = cv2.imread("data/%s" % path)

	# Not doing bg removal because its too challenging, cropping is unnecessary
	# borders = np.stack([
	# 	img[0:2, :, :],
	# 	img[-3:-1, :, :],
	# 	np.transpose(img[:, 0:2, :], axes=(1, 0, 2)),
	# 	np.transpose(img[:, -3:-1, :], axes=(1, 0, 2))
	# ])
	#
	# # Morphology stuff: https://stackoverflow.com/a/64492318
	# lower = np.min(borders, axis=(0, 1, 2))
	# upper = np.max(borders, axis=(0, 1, 2))
	#
	# thresh = cv2.inRange(img, lower, upper)
	#
	# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
	# morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
	#
	# mask = 255 - morph
	# img = cv2.bitwise_and(img, img, mask=mask)
	#
	# # Crop
	# vertical_pixel_sums = np.max(img, axis=(1, 2))
	# vertical_crops = np.arange(vertical_pixel_sums.shape[0])[vertical_pixel_sums != 0]
	#
	# hori_pixel_sums = np.max(img, axis=(0, 2))
	# hori_crops = np.arange(hori_pixel_sums.shape[0])[hori_pixel_sums != 0]
	#
	# crop_l_u = max(min(vertical_crops[0] - 1, hori_crops[0] - 1), 0)
	# crop_r_d = max(max(vertical_crops[-1] - 1, hori_crops[-1] - 1), 0)
	# print(crop_l_u, crop_r_d)
	#
	# img = img[crop_l_u:crop_r_d, crop_l_u:crop_r_d]

	# Resize for I-JEPA
	img = cv2.resize(img, (488, 488))

	# Save
	cv2.imwrite("data_processed/%s" % path, img)
