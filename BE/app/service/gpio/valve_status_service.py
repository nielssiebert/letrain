import RPi.GPIO as GPIO

from dev.BE.app.model.enums import Valve, ValveStatus
from app.service.gpio.pin_service import PinService

pin_service = PinService()

class NoGPIOPinAssignedException(Exception):
    pass

class ValveStatusService:
    def __init__(self):
        print("ValveStatusService initialized")

    def valve_switched_on(self, valve: Valve):
        self.ensure_io_pin_assigned(valve)
        
        pin_status = self.get_pin_status(valve.io_pin)

        if ((pin_status == GPIO.HIGH) and valve.high_to_switch_on) or ((pin_status == GPIO.LOW) and not valve.high_to_switch_on):
            return ValveStatus.ON
        else:
            return ValveStatus.OFF

    def set_valve_status(self, valve: Valve, status: ValveStatus):
        self.ensure_io_pin_assigned(valve)
        
        if status == ValveStatus.ON:
            pin_service.set_pin_status(valve.io_pin, GPIO.HIGH if valve.high_to_switch_on else GPIO.LOW)
        else:
            pin_service.set_pin_status(valve.io_pin, GPIO.LOW if valve.high_to_switch_on else GPIO.HIGH)
        

    def ensure_io_pin_assigned(self, valve):
        if valve.io_pin is None:
            raise NoGPIOPinAssignedException("Failure: No GPIO pin assigned to valve")