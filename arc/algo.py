# Imports
from PIL import ImageGrab, Image
import numpy as np
import serial
import time
import pyautogui as pyag
import dxcam

# testing: http://color.aurlien.net/#

# Variables
res = ImageGrab.grab().size  # Get the current resolution
screen_width = res[0]
screen_height = res[1]

led_count_h = 11        # Amount of leds ^^^
led_count_w = 2         # Amount of leds >>>

# const window size
h_bbox = screen_height // led_count_h
w_bbox = screen_width // led_count_w

# To fix non-integer window size
mod_h_bbox = screen_height % led_count_h
mod_w_bbox = screen_width % led_count_w

mod_h_ind = int(np.ceil(led_count_h / 2)) - 1
mod_w_ind = int(np.ceil(led_count_w / 2)) - 1

left_start = 0
top_start = 0
win_w = 0
win_h = 0

# Serial object
ser = serial.Serial('COM5', 115200)

# Setup a dxcam "camera"
camera = dxcam.create()
time.sleep(5)

while True:
	px = camera.grab()   # take a "screenshot"
	if px is None:
		continue

	idx = 0
	for row in range(led_count_h):
		if row == mod_h_ind and mod_h_bbox != 0:
			win_h = mod_h_bbox
		else:
			win_h = h_bbox

		for col in range(led_count_w):
			if col == mod_w_ind and mod_w_bbox != 0:
				win_w = mod_w_bbox
			else:
				win_w = w_bbox

			if row == 0 or row == led_count_h-1 or col == 0 or col == led_count_w-1:
				pic = px[top_start:top_start + win_h - 1, left_start:left_start + win_w - 1, :]
				print(top_start, top_start + win_h - 1, left_start, left_start + win_w - 1)
				# pic = camera.grab((left_start, top_start, left_start + win_w, top_start + win_h))
				# if pic is None:
				# 	continue

				data = [pic[:, :, 0].mean().astype(np.uint8), pic[:, :, 1].mean().astype(np.uint8), pic[:, :, 2].mean().astype(np.uint8)]
				time.sleep(0.001)
				ser.write(bytes([idx, data[0], data[1], data[2]]))
				idx += 1

			left_start += win_w

		top_start += win_h
		left_start = 0

	left_start = 0
	top_start = 0

# ser.close()

# TODO:
# 1. find alternative to ImageGarbage ## Changed the module from imagegarge to pyautogui,
#
