"""
TODO:
1. auto find specific arduino (serial COM)
2. improve latency - python/arduino?
3. test

Testing colors : http://color.aurlien.net/
Cool video for showoff: https://www.youtube.com/watch?v=74TAV9rnU10&list=RD74TAV9rnU10&start_radio=1&ab_channel=EugeneBelsky
"""

# Imports
from PIL import ImageGrab, Image    # Pillow
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

        self.serial_obj = ""

        self.led_count_h = ""
        self.led_count_w = ""

        self.init_position = ""
        self.init_positions = ("TL", "TR", "BR", "BL")
        self.sides = ("T", "R", "B", "L")

        self.screen_width = ""
        self.screen_height = ""

        self.win_height = ""
        self.win_width = ""

        self.win_height_res = ""
        self.win_width_res = ""

        self.win_list = []

        self.led_index = 0

    def set_serial_obj(self, obj):
        self.serial_obj = obj

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
        res = ImageGrab.grab().size
        self.screen_width = res[0]
        self.screen_height = res[1]
        return self.screen_width, self.screen_height

    def get_win_params(self):
        """
        Calculate windows possible sizes
        """
        self.win_height = self.screen_height // self.led_count_h
        self.win_width = self.screen_width // self.led_count_w

        self.win_height_res = self.screen_height % self.led_count_h
        self.win_width_res = self.screen_width % self.led_count_w

    def get_side_windows(self, side):
        side_win_list = []
        if side == self.sides[0]:
            # [T]op
            for i in range(self.led_count_w):
                # Create overlapping depends on pixels residue
                temp_left = i * self.win_width
                temp_right = temp_left + self.win_width + self.win_width_res - 1
                side_win_list.append([temp_left, 0, temp_right, self.win_height])

        elif side == self.sides[2]:
            # [B]ottom
            for i in range(self.led_count_w):
                # Create overlapping depends on pixels residue
                temp_right = self.screen_width - i*self.win_width - 1
                temp_left = temp_right - self.win_width - self.win_width_res + 1
                side_win_list.append([temp_left, self.screen_height-self.win_height, temp_right, self.screen_height-1])

        elif side == self.sides[1]:
            # [R]ight
            for i in range(self.led_count_h):
                # Create overlapping depends on pixels residue
                temp_top = i * self.win_height
                temp_bottom = temp_top + self.win_height + self.win_height_res - 1
                side_win_list.append([self.screen_width-self.win_width, temp_top, self.screen_width-1, temp_bottom])

        elif side == self.sides[3]:
            # [L]eft
            for i in range(self.led_count_h):
                # Create overlapping depends on pixels residue
                temp_bottom = self.screen_height - i * self.win_height - 1
                temp_top = temp_bottom - self.win_height - self.win_height_res + 1
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

    def calc_values(self):
        frame = self.camera.grab()
        if frame is None:
            return

        for i in range(0, len(self.win_list) - len(self.win_list) % 3, 3):
            data = []
            for j in range(3):
                c_frame = frame[self.win_list[i+j][1]:self.win_list[i+j][3], self.win_list[i+j][0]:self.win_list[i+j][2], :]
                data.append([i+j, c_frame[:, :, 0].mean().astype(np.uint8), c_frame[:, :, 1].mean().astype(np.uint8),
                             c_frame[:, :, 2].mean().astype(np.uint8)])

            data_send = [data[0][0], data[0][1], data[0][2], data[0][3],
                         data[1][0], data[1][1], data[1][2], data[1][3],
                         data[2][0], data[2][1], data[2][2], data[2][3]]

            time.sleep(0.0001)
            self.serial_obj.write_serial(data_send)
            time.sleep(0.02)

    def example_windows(self):
        frame = np.ones([self.screen_height, self.screen_width], dtype=np.uint8) * 255

        color = 20
        for positions in self.win_list:
            frame[positions[1], positions[0]:positions[2] + 1] = color
            frame[positions[3], positions[0]:positions[2] + 1] = color
            frame[positions[1]:positions[3] + 1, positions[0]] = color
            frame[positions[1]:positions[3] + 1, positions[2]] = color
            if color == 130:
                color = 20
            else:
                color = 130

        img = Image.fromarray(frame)
        img.show()

        # frame = self.camera.grab()
        # for positions in self.win_list:
        #     c_frame = frame[positions[1]:positions[3], positions[0]:positions[2]]
        #     img = Image.fromarray(c_frame)
        #     img.show()


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
                    return True
        else:
            print("No COM found!")
            return False

    def set_baudrate(self, baud_rate):
        self.baud_rate = baud_rate

    def init_com(self):
        try:
            self.obj = serial.Serial(self.com, self.baud_rate)
            time.sleep(1)
        except:
            print("Failed init COM communication")
            exit()

    def write_serial(self, data):
        self.obj.write(bytes(data))

    def read_serial(self):
        read = self.obj.read()
        return read


if __name__ == '__main__':

    serial_obj = SerialCom()
    if not serial_obj.find_arduino():
        exit()
    serial_obj.set_baudrate(250000)
    serial_obj.init_com()

    leds_control = LedsControl()
    time.sleep(3)

    leds_control.set_serial_obj(serial_obj)
    leds_control.set_leds_count(15, 8)
    leds_control.set_position("BL")
    leds_control.get_screen_res()
    leds_control.create_win_list()
    # leds_control.example_windows()

    while True:
        leds_control.calc_values()
