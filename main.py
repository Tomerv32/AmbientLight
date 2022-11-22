"""
TODO:
1. auto find specific arduino (serial COM)

Testing colors : http://color.aurlien.net/
Cool video for showoff: https://www.youtube.com/watch?v=74TAV9rnU10&list=RD74TAV9rnU10&start_radio=1&ab_channel=EugeneBelsky
"""

# Imports
from PIL import Image    # Pillow
import numpy as np
import serial                       # pyserial
import serial.tools.list_ports
import time
import dxcam


class LedsControl:
    def __init__(self):
        """
        Init function for LED strip algorithm
        """
        self.camera = dxcam.create()
        self.serial_obj = SerialCom()

        self.led_count_h = None
        self.led_count_w = None

        self.init_position = None
        self.init_positions = ("TL", "TR", "BR", "BL")
        self.sides = ("T", "R", "B", "L")

        self.screen_width = None
        self.screen_height = None

        self.led_update_tol = None
        self.led_tol_list = None

        self.win_height = None
        self.win_width = None

        self.win_height_mod = None
        self.win_width_mod = None

        self.win_list = []


    def set_serial_obj(self, baud_rate):
        self.serial_obj.find_arduino()
        self.serial_obj.set_baud_rate(baud_rate)
        self.serial_obj.init_com()

    def set_leds_count(self, leds_height, leds_width):
        """
        int led_width:      LEDs count on upper and lower sides
        int led_height:     LEDs count on left and right sides
        """
        self.led_count_h = leds_height
        self.led_count_w = leds_width

    def set_position(self, pos):
        """
        BL, TL, TR, BR
        """
        self.init_position = pos

    def get_screen_res(self):
        """
        Get screen resolution to calc windows sizes

        `int` return: screen width, screen height
        """
        res_img = self.camera.grab()
        self.screen_height, self.screen_width, _ = res_img.shape

        return self.screen_width, self.screen_height

    def set_led_update_tol(self, tol):
        self.led_update_tol = tol
        self.led_tol_list = [tol] * 3 + [-tol] * 3

    def get_win_params(self):
        """
        Calculate windows possible sizes
        """
        self.win_height = self.screen_height // self.led_count_h
        self.win_width = self.screen_width // self.led_count_w

        self.win_height_mod = self.screen_height % self.led_count_h
        self.win_width_mod = self.screen_width % self.led_count_w

    def get_side_windows(self, side):
        """
        Calculate the windows for each LED

        Some +/-1 adjustments were made to create a proper overlapping
        and avoiding IndexError (indexing outside the list bounds)
        *** see self.example_windows(bool: show_windows, bool: show_frame) for visuals

        Corner are calculated twice, for both width/height corner leds
        """
        side_win_list = []
        if side == self.sides[0]:
            # [T]op
            for i in range(self.led_count_w):
                # Create overlapping depends on pixels residue
                temp_left = i*self.win_width
                temp_right = temp_left + self.win_width + self.win_width_mod - 1
                side_win_list.append([temp_left, 0, temp_right, self.win_height-1])

        elif side == self.sides[2]:
            # [B]ottom
            for i in range(self.led_count_w):
                # Create overlapping depends on pixels residue
                temp_right = self.screen_width - 1 - i*self.win_width
                temp_left = temp_right - self.win_width - self.win_width_mod + 1
                side_win_list.append([temp_left, self.screen_height-self.win_height, temp_right, self.screen_height-1])

        elif side == self.sides[1]:
            # [R]ight
            for i in range(self.led_count_h):
                # Create overlapping depends on pixels residue
                temp_top = i*self.win_height
                temp_bottom = temp_top + self.win_height + self.win_height_mod - 1
                side_win_list.append([self.screen_width-1-self.win_width, temp_top, self.screen_width-1, temp_bottom])

        elif side == self.sides[3]:
            # [L]eft
            for i in range(self.led_count_h):
                # Create overlapping depends on pixels residue
                temp_bottom = self.screen_height - 1 - i*self.win_height
                temp_top = temp_bottom - self.win_height - self.win_height_mod + 1
                side_win_list.append([0, temp_top, self.win_width, temp_bottom])

        return side_win_list

    def create_win_list(self):
        self.get_win_params()

        if self.init_position == self.init_positions[0]:
            self.win_list.extend(self.get_side_windows("T"))
            self.win_list.extend(self.get_side_windows("R"))
            self.win_list.extend(self.get_side_windows("B"))
            self.win_list.extend(self.get_side_windows("L"))

        elif self.init_position == self.init_positions[1]:
            # TR
            self.win_list.extend(self.get_side_windows("R"))
            self.win_list.extend(self.get_side_windows("B"))
            self.win_list.extend(self.get_side_windows("L"))
            self.win_list.extend(self.get_side_windows("T"))

        elif self.init_position == self.init_positions[2]:
            # BR
            self.win_list.extend(self.get_side_windows("B"))
            self.win_list.extend(self.get_side_windows("L"))
            self.win_list.extend(self.get_side_windows("T"))
            self.win_list.extend(self.get_side_windows("R"))

        elif self.init_position == self.init_positions[3]:
            # BL
            self.win_list.extend(self.get_side_windows("L"))
            self.win_list.extend(self.get_side_windows("T"))
            self.win_list.extend(self.get_side_windows("R"))
            self.win_list.extend(self.get_side_windows("B"))

    def loop_calc_send_values(self):
        old_data = [[-1000] * 3] * len(self.win_list)
        old_screenshot = ""
        while True:
            for led_index in range(len(self.win_list)):
                screenshot = self.camera.grab()
                if screenshot is not None:
                    old_screenshot = screenshot
                else:
                    screenshot = old_screenshot

                win = screenshot[self.win_list[led_index][1]:self.win_list[led_index][3],
                      self.win_list[led_index][0]:self.win_list[led_index][2], :]

                # # Mean Value
                data = [led_index, *np.average(win, axis=(0, 1)).astype(np.uint8)]

                # Median Value
                # data = [led_index, *np.median(win, axis=(0, 1)).astype(np.uint8)]

                # Only update if color has changed, more than given tolerance
                if not ((np.add(old_data[led_index], self.led_tol_list[:3]) > data[1:]).all() and
                        (np.add(old_data[led_index], self.led_tol_list[3:]) < data[1:]).all()):
                    old_data[led_index] = data[1:]
                    self.serial_obj.write_serial(data)
                    time.sleep(0.004)

    def example_windows(self, show_windows=True, show_frame=False):
        """
        Plots the windows used for LED color calculations
        # USE Pillow==9.3.0
        """

        if show_windows:
            frame_windows = np.zeros([self.screen_height, self.screen_width, 3], dtype=np.uint8)
            layers = [0, 1, 2]
            layers_idx = 0
            for positions in self.win_list:
                frame_windows[positions[1], positions[0]:positions[2], layers[layers_idx]] = 255
                frame_windows[positions[3], positions[0]:positions[2], layers[layers_idx]] = 255
                frame_windows[positions[1]:positions[3], positions[0], layers[layers_idx]] = 255
                frame_windows[positions[1]:positions[3], positions[2], layers[layers_idx]] = 255

                layers_idx += 1
                if layers_idx == len(layers):
                    layers_idx = 0

            frame_wins = Image.fromarray(frame_windows)
            frame_wins.show()

        if show_frame:
            frame = None
            while frame is None:
                frame = self.camera.grab()

            frame_screenshot = np.zeros([self.screen_height, self.screen_width, 3], dtype=np.uint8)

            for positions in self.win_list:
                frame_screenshot[positions[1]:positions[3], positions[0]:positions[2], :] =\
                    frame[positions[1]:positions[3], positions[0]:positions[2], :]

            frame_screens = Image.fromarray(frame_screenshot)
            frame_screens.show()


class SerialCom:
    def __init__(self):
        self.baud_rate = ""
        self.com = ""
        self.obj = None

    def find_arduino(self):
        # should improve - find specific arduino..
        ports = list(serial.tools.list_ports.comports())
        if ports:
            for p in ports:
                if p.manufacturer == "wch.cn":
                    self.com = p.name
        else:
            print("No COM found!")
            exit()

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate

    def init_com(self):
        try:
            self.obj = serial.Serial(self.com, self.baud_rate)
        except:
            print("Failed init COM communication")
            exit()

    def write_serial(self, data):
        self.obj.write(bytes(data))

    def read_serial(self):
        read = self.obj.read()
        return read


if __name__ == '__main__':
    # user params #
    user_baud_rate = 9600
    user_led_count_height = 17
    user_led_count_width = 33
    user_zeroth_led_position = "BL"
    user_led_update_tolerance = 15
    ###############

    leds_control = LedsControl()
    leds_control.set_serial_obj(user_baud_rate)
    leds_control.set_leds_count(user_led_count_height, user_led_count_width)
    leds_control.set_position(user_zeroth_led_position)
    leds_control.get_screen_res()
    leds_control.set_led_update_tol(user_led_update_tolerance)
    leds_control.create_win_list()
    # leds_control.example_windows(show_windows=True, show_frame=True)
    time.sleep(2)

    leds_control.loop_calc_send_values()
