from .. import db
from .associations import trigger_factor_association, valve_trigger_association

class Trigger(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=True)
    time = db.Column(db.Time, nullable=True)
    weekdays = db.Column(db.JSON, nullable=True)
    from_date = db.Column(db.Date, nullable=True)
    to_date = db.Column(db.Date, nullable=True)
    duration = db.Column(db.DateTime, nullable=False)
    valves = db.relationship('Valve', secondary=valve_trigger_association, back_populates='triggers')
    factors = db.relationship('Factor', secondary=trigger_factor_association, back_populates='triggers')