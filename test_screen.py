# Minimal screen test - upload as main.py
from machine import SPI, Pin
import st7789

spi = SPI(0, baudrate=40000000, polarity=1, phase=0, bits=8, endia=0, sck=Pin(6), mosi=Pin(8))
display = st7789.ST7789(spi, 240, 240, reset=Pin(11, func=Pin.GPIO, dir=Pin.OUT), dc=Pin(7, func=Pin.GPIO, dir=Pin.OUT))
display.init()

# Fill red to test
display.fill(st7789.color565(255, 0, 0))
