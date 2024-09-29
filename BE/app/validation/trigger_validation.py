# validators.py
from marshmallow import ValidationError
from ..model.trigger import Trigger

def validate_triggers_exist(triggers):
    missing_triggers = []
    for trigger in triggers:
        if not Trigger.query.filter_by(name=trigger).first():
            missing_triggers.append(trigger)
    if missing_triggers:
        raise ValidationError(f"Triggers not found: {', '.join(missing_triggers)}")