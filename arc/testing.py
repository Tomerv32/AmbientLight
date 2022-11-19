# Imports
from PIL import ImageGrab, Image
import numpy as np
import serial
import time
import dxcam
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# testing: http://color.aurlien.net/#

# Variables
res = ImageGrab.grab().size  # Get the current resolution
screen_width = res[0]
screen_height = res[1]

led_count_h = 6  # Amount of leds ^^^
led_count_w = 6  # Amount of leds >>>

# const window size
h_bbox = screen_height // led_count_h  # divide the screen height (1080) by the led count (`led_count_h`)
w_bbox = screen_width // led_count_w  # divide the screen width (1920) by the led count (`led_count_w`)

# To fix non-integer window size
mod_h_bbox = screen_height % led_count_h
mod_w_bbox = screen_width % led_count_w

mod_h_int = int(np.ceil(led_count_h / 2)) - 1
mod_w_int = int(np.ceil(led_count_w / 2)) - 1

left_start = 0
top_start = 0
win_w = 0
win_h = 0

# data = [[0 for x in range(led_count_w)] for y in range(led_count_h)]
blocks = list()

#####################

win_h = h_bbox
# Go over all available windows at the top of the screen (starting from left to right)
for col in range(led_count_w):
    if col == mod_w_int and mod_w_bbox != 0:
        win_w = mod_w_bbox
    else:
        win_w = w_bbox

    blocks.append([top_start, top_start + win_h - 1, left_start, left_start + win_w - 1])
    left_start += win_w

#####################

left_start -= win_w
for row in range(led_count_h):
    if row == mod_h_int and mod_h_bbox != 0:
        win_h = mod_h_bbox
    else:
        win_h = h_bbox

    blocks.append([top_start, top_start + win_h - 1, left_start, left_start + win_w - 1])
    top_start += win_h

#####################

top_start -= win_h
for col in reversed(range(led_count_w)):
    if col == mod_w_int and mod_w_bbox != 0:
        win_w = mod_w_bbox
    else:
        win_w = w_bbox

    blocks.append([top_start, top_start + win_h - 1, left_start, left_start + win_w - 1])
    left_start -= win_w

#####################

left_start += win_w
for row in reversed(range(led_count_h)):
    if row == mod_h_int and mod_h_bbox != 0:
        win_h = mod_h_bbox
    else:
        win_h = h_bbox

    blocks.append([top_start, top_start + win_h - 1, left_start, left_start + win_w - 1])
    top_start -= win_h
# Shai's testing


# Serial object
ser = serial.Serial('COM5', 250000)

# Setup a dxcam "camera"
camera = dxcam.create()
time.sleep(5)

while True:
    px = camera.grab()  # take a "screenshot"
    if px is None:
        continue

    idx = 0
    for i in range(0, len(blocks) - len(blocks) % 3, 3):
        vals = blocks[i]
        pic = px[vals[0]:vals[1], vals[2]:vals[3], :]
        data = [pic[:, :, 0].mean().astype(np.uint8), pic[:, :, 1].mean().astype(np.uint8),
                pic[:, :, 2].mean().astype(np.uint8)]

        vals = blocks[i + 1]
        pic = px[vals[0]:vals[1], vals[2]:vals[3], :]
        data1 = [pic[:, :, 0].mean().astype(np.uint8), pic[:, :, 1].mean().astype(np.uint8),
                 pic[:, :, 2].mean().astype(np.uint8)]

        vals = blocks[i + 2]
        pic = px[vals[0]:vals[1], vals[2]:vals[3], :]
        data2 = [pic[:, :, 0].mean().astype(np.uint8), pic[:, :, 1].mean().astype(np.uint8),
                 pic[:, :, 2].mean().astype(np.uint8)]

        time.sleep(0.0001)
        ser.write(bytes(
            [idx, data[0], data[1], data[2], idx + 1, data1[0], data1[1], data1[2], idx + 2, data2[0], data2[1],
             data2[2]]))
        idx += 3

# time.sleep(1000)

# TODO:
# Move to algo.py
# Check index/%, verify it works for every number!!! (i+2)
# Move first LED to bottom-left
# Set window height/width to const! (?)
# Windows service to run py script
# Check ref value in case of bright colors (orange? white?)
# Better way to calc colors
# Test sending more RGB values to arduino in a single write
# Auto find arduino com
