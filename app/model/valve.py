from .. import db
from .associations import valve_trigger_association
from marshmallow import Schema, fields, validate, ValidationError

class Valve(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    io_pin = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('ON', 'OFF'), default='OFF')
    high_to_switch_on = db.Column(db.Boolean, default=True)
    triggers = db.relationship('Trigger', secondary=valve_trigger_association, back_populates='valves')

class ValveSchema(Schema):
    id = fields.Str(required=True, validate=validate.Length(min=1))
    name = fields.Str(required=True, validate=validate.Length(min=1))
    io_pin = fields.Int(required=True)
    status = fields.Str(required=False, dump_only=True)
    high_to_switch_on = fields.Bool(required=True)
    triggers = fields.List(fields.Str(validate=validate.Validator), required=True)