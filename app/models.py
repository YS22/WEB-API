 # -*- coding: utf-8 -*-
from hashlib import md5
from app import db
# from werkzeug.security import generate_password_has, check_password_hash
registrations = db.Table('registrations',
db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class User(db.Model):
    id = db.Column(db.String, primary_key = True)
    nickname = db.Column(db.String, index = True, unique = True)
    gender=db.Column(db.String)
    avatarUrl=db.Column(db.String)
    tel=db.Column(db.String(11))
    latitude=db.Column(db.String)
    longitude=db.Column(db.String)
    state=db.Column(db.String)
    group = db.relationship('Group',secondary=registrations,backref=db.backref('user', lazy='dynamic'),lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    createrId=db.Column(db.String)
    createTime=db.Column(db.Date)

class Inspect(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    groupid=db.Column(db.String)
    createrid=db.Column(db.String)
    userid=db.Column(db.String)
    time=db.Column(db.Date)