#!/usr/bin/python
# Example using a character LCD connected to a Raspberry Pi or BeagleBone Black.

import datetime
import time
import socket

import Adafruit_CharLCD as LCD


class LCDC:
    def __init__(self):
        # Raspberry Pi pin configuration:
        self.lcd_rs = 25  # Note this might need to be changed to 21 for older revision Pi's.
        self.lcd_en = 24
        self.lcd_d4 = 23
        self.lcd_d5 = 17
        self.lcd_d6 = 12
        self.lcd_d7 = 22
        self.lcd_backlight = 4

        # Define LCD column and row size for 16x2 LCD.
        self.lcd_columns = 16
        self.lcd_rows = 2

        # Initialize the LCD using the pins above.
        self.lcd = LCD.Adafruit_CharLCD(self.lcd_rs, self.lcd_en, self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7,
                                        self.lcd_columns, self.lcd_rows, self.lcd_backlight)
        self.lcd.clear()

if __name__ == "__main__":
    # Print a two line message
    def date(self):
        self.lcd.message(str(datetime.date.today()) + "\n" + str(datetime.datetime.now().strftime('%H:%M:%S')))



