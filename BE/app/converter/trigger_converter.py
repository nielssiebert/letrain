from ..model.enums import Trigger

class TriggerConverter:
    pass
    
    def to_dict(self, trigger: Trigger):
        return {
            'id': trigger.id,
            'name': trigger.name,
            'date': trigger.date,
            'time': trigger.time,
            'weekdays': trigger.weekdays,
            'from_date': trigger.from_date,
            'to_date': trigger.to_date,
            'duration': trigger.duration,
            'valves': [valve.id for valve in trigger.valves],
            'factors': [factor.id for factor in trigger.factors]
        }