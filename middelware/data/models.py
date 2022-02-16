from .db import db
import mongoengine_goodjson as gj

class ValveTime(gj.EmbeddedDocument):
    h = db.IntField(required=True)
    m = db.IntField(required=True)
    s = db.IntField(required=True)
    
class Valve(gj.Document):
    name = db.StringField(required=True)
    activated = db.BooleanField(required=True)
    timer = db.EmbeddedDocumentField(ValveTime, default=ValveTime)