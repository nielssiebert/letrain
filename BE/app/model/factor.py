from .. import db
from .associations import trigger_factor_association

class Factor(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    factor = db.Column(db.Float, default=1.0)
    triggers = db.relationship('Trigger', secondary=trigger_factor_association, back_populates='factors')