# Imports
import cv2
import numpy as np

from os import listdir
from os.path import isfile, join


def rm_img_bg_by_center(img):
	# See what color the corners of the image are
	center = (img.shape[0]//2, img.shape[1]//2)
	center = img[center[0] - 15:center[0] + 15, center[1] - 15:center[1] + 15]

	# Morphology stuff: https://stackoverflow.com/a/64492318
	lower = np.median(center, axis=(0, 1)) * .9
	upper = np.median(center, axis=(0, 1)) * 1.1

	thresh = cv2.inRange(img, lower, upper)

	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
	morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

	return cv2.bitwise_and(img, img, mask=morph)


def rm_img_bg(img):
	# See what color the corners of the image are
	corners = np.stack([
		img[0:10, 0:10, :],
		img[0:10, -11:-1, :],
		img[-11:-1, 0:10, :],
		img[-11:-1, -11:-1, :],
		# np.transpose(img[:, 0:5, :], axes=(1, 0, 2)),
		# np.transpose(img[:, -6:-1, :], axes=(1, 0, 2)),
	])

	# Morphology stuff: https://stackoverflow.com/a/64492318
	lower = np.median(corners, axis=(0, 1, 2)) * .9
	upper = np.median(corners, axis=(0, 1, 2)) * 1.1

	thresh = cv2.inRange(img, lower, upper)

	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
	morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

	mask = 255 - morph
	return cv2.bitwise_and(img, img, mask=mask)


def rm_img_bg_outside_range(img, lower, upper):
	thresh = cv2.inRange(img, lower, upper)

	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
	morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

	return cv2.bitwise_and(img, img, mask=morph)


def get_img_crops(img_no_bg):
	vertical_pixel_sums = np.max(img_no_bg, axis=(1, 2))
	vertical_crops = np.arange(vertical_pixel_sums.shape[0])[vertical_pixel_sums != 0]

	hori_pixel_sums = np.max(img_no_bg, axis=(0, 2))
	hori_crops = np.arange(hori_pixel_sums.shape[0])[hori_pixel_sums != 0]

	if len(vertical_crops) < 1:
		vertical_crops = (0, img_no_bg.shape[0])
	if len(hori_crops) < 1:
		hori_crops = (0, img_no_bg.shape[1])

	return vertical_crops[0] - 1, hori_crops[0] - 1, vertical_crops[-1] - 1, hori_crops[-1] - 1


if __name__ == "__main__":
	# Process all files in directory
	only_files = [f for f in listdir("data/") if isfile(join("data/", f))]

	for path in only_files:
		print(path)
		img = cv2.imread("data/%s" % path)

		if path.endswith("fb.png"):
			img_height, img_width, _ = img.shape
			img_height *= 488 / img_width
			cv2.imwrite("data_processed/%sfb-unedited.png" % path[:-6], cv2.resize(img, (488, int(img_height))))

		# Remove bg
		img_no_bg = rm_img_bg(img)

		# Crop
		vert_1, hori_1, vert_2, hori_2 = get_img_crops(img_no_bg)

		crop_l_u = max(min(vert_1, hori_1), 0)
		crop_r_d = max(max(vert_2, hori_2), 0)

		img = img[crop_l_u:crop_r_d, crop_l_u:crop_r_d]

		# Resize for I-JEPA
		img = cv2.resize(img, (488, 488))

		# Save
		cv2.imwrite("data_processed/%s" % path, img)
