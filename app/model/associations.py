from .. import db

valve_trigger_association = db.Table('valve_trigger_association',
    db.Column('valve_id', db.String, db.ForeignKey('valve.id'), primary_key=True),
    db.Column('trigger_id', db.String, db.ForeignKey('trigger.id'), primary_key=True)
)

trigger_factor_association = db.Table('trigger_factor_association',
    db.Column('trigger_id', db.String, db.ForeignKey('trigger.id'), primary_key=True),
    db.Column('factor_id', db.String, db.ForeignKey('factor.id'), primary_key=True)
)