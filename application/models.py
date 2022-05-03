from .database import db
from flask_login import UserMixin


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(200),unique=True)
    password = db.Column(db.String(200))
    tracker = db.relationship("Tracker")
    log = db.relationship("Log")

class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    description = db.Column(db.String(200))
    tracker_type = db.Column(db.String(200))
    setting = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    log = db.relationship("Log")
    
class Log(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    timestamp = db.Column(db.String(200))
    added_date_time = db.Column(db.String(200))
    value = db.Column(db.Integer)
    notes = db.Column(db.String(200))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    tracker_id = db.Column(db.Integer,db.ForeignKey('tracker.id'))
