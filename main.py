from flask import Flask
# from google.cloud.sql.connector import Connector, IPTypes
from flask_sqlalchemy import SQLAlchemy

import os

from google.cloud.sql.connector import Connector, IPTypes
from google.cloud.sql.connector import connector
import pg8000

import sqlalchemy

import config
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

db_user = config.username
db_pass = config.password
db_name = config.db_name
instance_connection_name = config.connection_name
ip_type = IPTypes.PUBLIC

def getconn():
    with Connector() as connector:
        conn = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "creator": getconn
}
db = SQLAlchemy(app)

class Classes(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    full_name=db.Column(db.String(255), nullable=True)
    abbr_name=db.Column(db.String(255), nullable=True)
    credits=db.Column(db.Integer, nullable=True)
    semester=db.Column(db.String(255), nullable=True) # Fall, FallSpring, Spring
    prereq_id_list=db.Column(MutableList.as_mutable(PickleType), default=[])
    offering_id_list=db.Column(MutableList.as_mutable(PickleType), default=[])
    # prereqs=db.relationship('Classes', backref='prereqs', lazy=True)
    # offerings=db.relationship('CourseOfferings', backref='offerings', lazy=True)
    school=db.relationship('Schools', backref=db.backref('classes', lazy=True))
    school_id=db.Column(db.Integer, db.ForeignKey('schools.id'))

class Schools(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(255))
    # classes=db.relationship('Classes', backref='classes', lazy=True)

class CourseOfferings(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    latitute=db.Column(db.Float, nullable=True)
    longitute=db.Column(db.Float, nullable=True)
    start_time=db.Column(db.Time, nullable=True)
    end_time=db.Column(db.Time, nullable=True)
    semester=db.Column(db.String(255), nullable=True)
    year=db.Column(db.Integer, nullable=True)
    prof=db.Column(db.String(255), nullable=True)
    school=db.relationship('Schools', backref=db.backref('courseofferings', lazy=True))
    school_id=db.Column(db.Integer, db.ForeignKey('schools.id'))
    # school=db.relationship('Schools', backref='school_id', lazy=True)
class Curriculum(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(255), nullable=True)
    class_id_list=db.Column(MutableList.as_mutable(PickleType), default=[])
    group_id_list=db.Column(MutableList.as_mutable(PickleType), default=[])
    school=db.relationship('Schools', backref=db.backref('curriculum', lazy=True))
    school_id=db.Column(db.Integer, db.ForeignKey('schools.id'))
    # school=db.relationship('Schools', backref='school_id', lazy=True)
    # classes=db.relationship('Classes', backref='classes', lazy=True)
    # groups=db.relationship('CourseGroups', backref='groups', lazy=True)
    # school=db.relationship('Schools', backref='school_id', lazy=True)
class CourseGroups(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(255), nullable=True)
    class_list=db.Column(MutableList.as_mutable(PickleType), default=[])
# db.create_all()
# db
# # print(db)
# # with db.connect() as conn:
#     # conn.execute("CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY, name varchar(255) NOT NULL, email varchar(255) NOT NULL)")
# # print(db.execute("SELECT * FROM users").fetchall())

from read_data import *

def reset_db():
    with app.app_context():
        db.session.commit()
        db.drop_all()
        db.create_all()
        db.session.commit()
        
def seed_db():
    with app.app_context():
        s = Schools(name="University of Kansas", id=1)
        db.session.add(s)
        db.session.commit()
        
        # c = Classes(full_name="Programming I", abbr_name="EECS 168", credits=4, semester=1, school_id=s.id)
        # db.session.add(c)
        # db.session.commit()
        classes, offerings = get_data()
        
        
        for i in range(len(offerings)):
            # cl = CourseOfferings(full_name=offerings.iloc[i]['full_name'], abbr_name=offerings.iloc[i]['abbr_name'], credits=offerings.iloc[i]['credits'], semester=offerings.iloc[i]['semester'], school_id=offerings.iloc[i]['school_id'])
            course_offering = CourseOfferings(start_time=offerings.iloc[i]['Start'], end_time=offerings.iloc[i]['End'], semester=offerings.iloc[i]['semester'], year=offerings.iloc[i]['year'], prof=offerings.iloc[i]['prof'], school_id=offerings.iloc[i]['school_id'])
            db.session.add(course_offering)
            
            class_data = classes[classes['abbr_name'] == offerings.iloc[i]['abbr_name']]
            print(class_data)
            cl = Classes.query.filter(Classes.abbr_name == offerings.iloc[i]['abbr_name']).all()
            
            print("cl " + str(cl))
            if cl != []:
                cl = cl.first()
                print(type(cl.offering_id_list))
                cl.offering_id_list += course_offering.id
            else:
                # course = Classes(full_name=class_data['full_name'], abbr_name=class_data['abbr_name'], credits=class_data['credits'], semester=class_data['semester'], school_id=class_data['school_id'])
                course = Classes(full_name=class_data['full_name'], school_id=class_data['school_id'])
                # course.offering_id_list.append(course_offering.id)
                if course.offering_id_list:
                    course.offering_id_list += course_offering.id
                else:
                    course.offering_id_list = [course_offering.id]
                db.session.add(course)
            # db.session.commit()
            
            
            
        db.session.commit()
        
        print(Classes.query.all())

@app.route('/')
def hello_world():
    with app.app_context():
        # print(Users.query.all())
        # u = Users(id=3)
        # db.session.add(u)
        # db.session.commit()
        # print(Users.query.all())
        # return str(Users.query.all())
        return str(Classes.query.all())