from ..model.valve import Valve

class ValveConverter:
    pass

    def to_dict(self, valve: Valve):
        return {
            'id': self.id,
            'name': valve.name,
            'status': valve.status,
            'io_pin': self.io_pin,
            'high_to_switch_on': self.high_to_switch_on,
            'triggers': [trigger.id for trigger in self.triggers]
        }