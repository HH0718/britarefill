from neopixel import *
import time
import os
import RPi.GPIO as GPIO
import lcd

LCD = lcd.LCDC()

LED_COUNT = 2
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 250  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP = ws.WS2811_STRIP_RGB  # Strip type and colour ordering

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LED1 = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
                         LED_STRIP)
LED1.begin()
LED1.setPixelColorRGB(0, 0, 85, 0)
LED1.show()
LED2 = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
                         LED_STRIP)

LED1.setPixelColorRGB(1, 85, 0, 0)
LED1.show()
DEBUG = True


def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if (adcnum > 7) or (adcnum < 0):
        return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)  # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3  # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1  # first bit is 'null' so drop it
    return adcout


SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8
RELAY = 22

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(RELAY, GPIO.OUT)
GPIO.output(RELAY, False)

water_sensor = 1

last_read = 0  # this keeps track of the water sensor value
tolerance = 5  # to keep from being jittery we'll only change
# volume when the sensor has moved more than 5 'counts'
pump_active = False
try:
    while True:
        # we'll assume that the water level didn't change
        water_level_change = False
        LCD.lcd.home()

        # print(pump_active)

        # read the analog pin
        water_level = readadc(water_sensor, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # how much has it changed since the last read?
        level_change = abs(water_level - last_read)

        if DEBUG:
            print("Water level:", water_level)
            print("water level change:", level_change)
            print("last_read", last_read)

        if level_change > tolerance:
            water_level_change = True

        if DEBUG:
            print(
                "Water Level Changed", water_level_change)

        if water_level_change or water_level < 10:
            current_water_level = (water_level / 10.24)  # convert 10bit adc0 (0-1024) water level read into 0-100 level
            current_water_level = round(current_water_level)  # round out decimal value
            current_water_level = int(current_water_level)  # cast level as integer

            if DEBUG:
                print('level = {level}'.format(level=current_water_level))

            if DEBUG:
                print("set_volume", current_water_level)
                print("tri_pot_changed", current_water_level)
            if current_water_level <= 50:

                if not pump_active:
                    LCD.lcd.home()
                    LCD.lcd.message('Water LVL @{}\nActivating Pump'.format(current_water_level))
                pump_active = True
                GPIO.output(RELAY, True)
            elif current_water_level > 50:
                if pump_active and current_water_level >= 90:
                    pump_active = False
                    GPIO.output(RELAY, False)
                    LCD.lcd.home()
                    LCD.lcd.message('Water LVL @{}\nDeactivating Pump'.format(current_water_level))
                    LCD.lcd.clear()

            # save the potentiometer reading for the next loop
        last_read = water_level
        # LCD.lcd.message('Level @ {}%'.format(water_level))

        # hang out and do nothing for a half second
        time.sleep(1)
except:
    LED1.setBrightness(0)
    LED1.show()
    LED2.setBrightness(0)
    LED2.show()
    GPIO.cleanup()
