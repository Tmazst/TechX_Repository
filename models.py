
# from alchemy_db import db.Model
from sqlalchemy import  MetaData, ForeignKey
from flask_login import login_user, UserMixin
from sqlalchemy.orm import backref, relationship
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
# from app import app

db = SQLAlchemy()


#from app import login_manager

metadata = MetaData()



#Users class, The class table name 'h1t_users_cvs'
class User(db.Model,UserMixin):


    # __table_args__ = {'extend_existing': True}

    #Create db.Columns
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
    image = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120), unique=True)
    confirm_password = db.Column(db.String(120), unique=True)
    verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(120))
    projects = relationship("Curr_Projects",backref="Curr_Projects",lazy=True)
    project_briefs = relationship("Project_Brief", backref="Project_Brief", lazy=True)


    __mapper_args__={
        "polymorphic_identity":'user',
        'polymorphic_on':role
    }


class Project_Brief(db.Model,UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,ForeignKey('user.id'))
    name = db.Column(db.String(120))
    brief_date = db.Column(db.String(120))
    token = db.Column(db.String(120))



class Curr_Projects(db.Model,UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    name = db.Column(db.String(120))
    deposit = db.Column(db.Numeric(20))
    installments = db.Column(db.Numeric(20))
    proj_charge = db.Column(db.Numeric(20))
    proj_started = db.Column(db.Date())
    proj_deadline = db.Column(db.Date())
    comments = db.Column(db.String(120))
    submitted = db.Column(db.Date())


