import RPi.GPIO as GPIO

class PinService:
    def __init__(self):
        print("PinService initialized")

    def get_pin_status(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)
        pin_status = GPIO.input(pin)
        GPIO.cleanup()
        return pin_status
    
    def set_pin_status(self, pin, status):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, status)
        GPIO.cleanup()
        return