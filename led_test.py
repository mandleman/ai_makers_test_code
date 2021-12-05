import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup([17,27,22], GPIO.OUT)
GPIO.setup([3], GPIO.IN)
red=17
yellow=27
green=22
def set_color(color):
    GPIO.output(17,GPIO.LOW)
    GPIO.output(27,GPIO.LOW)
    GPIO.output(22,GPIO.LOW)
    GPIO.output(color,GPIO.HIGH)

try:
    while 1:
        set_color(red)
        time.sleep(1)
        set_color(yellow)
        time.sleep(1)
        set_color(green)
        time.sleep(1)
finally:
        GPIO.cleanup()
