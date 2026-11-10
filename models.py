
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


class client_user(User):

    id = db.Column(db.Integer, ForeignKey('user.id'), primary_key=True)
    contacts = db.Column(db.String(20))
    date_of_birth = db.Column(db.DateTime())
    address = db.Column(db.String(120))
    other = db.Column(db.String(120)) #Resume
    # jobs_applied_for = relationship("Applications", backref='Applications.job_title', lazy=True)
    # hired_user = relationship("hired", backref='Hired Applicant', lazy=True)

    __mapper_args__={
            "polymorphic_identity":'client_user'
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


class CashBook(db.Model,UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.DateTime())
    description = db.Column(db.String(120))
    amount = db.Column(db.Float)
    exp_or_income = db.Column(db.String(120))
    timestamp = db.column(db.DateTime())

class DomainRequest(db.Model):
    __tablename__ = 'domain_request'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    requested_label = db.Column(db.String(63), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    request_type = db.Column(db.String(40), nullable=False)
    intended_use = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    admin_notes = db.Column(db.String(500), nullable=True)

    @property
    def fqdn(self):
        return f'{self.requested_label}.eswtn.com'

class DomainAccount(db.Model):
    __tablename__ = 'domain_account'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('domain_request.id'), nullable=False, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    owner_email = db.Column(db.String(120), nullable=False, index=True)
    label = db.Column(db.String(63), nullable=False, unique=True, index=True)
    fqdn = db.Column(db.String(255), nullable=False, unique=True, index=True)
    plan = db.Column(db.String(40), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active', index=True)
    record_limit = db.Column(db.Integer, nullable=False, default=25)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    activated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    records = db.relationship(
        'ManagedDnsRecord',
        backref='domain_account',
        lazy=True,
        cascade='all, delete-orphan'
    )
    audit_logs = db.relationship(
        'DnsAuditLog',
        backref='domain_account',
        lazy=True,
        cascade='all, delete-orphan'
    )


class ManagedDnsRecord(db.Model):
    __tablename__ = 'managed_dns_record'

    id = db.Column(db.Integer, primary_key=True)
    domain_account_id = db.Column(db.Integer, db.ForeignKey('domain_account.id'), nullable=False, index=True)
    provider_record_id = db.Column(db.String(64), nullable=False, unique=True, index=True)
    record_type = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(255), nullable=False, index=True)
    content = db.Column(db.String(2048), nullable=False)
    ttl = db.Column(db.Integer, nullable=False, default=1)
    proxied = db.Column(db.Boolean, nullable=False, default=False)
    priority = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class DnsAuditLog(db.Model):
    __tablename__ = 'dns_audit_log'

    id = db.Column(db.Integer, primary_key=True)
    domain_account_id = db.Column(db.Integer, db.ForeignKey('domain_account.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    action = db.Column(db.String(40), nullable=False, index=True)
    record_name = db.Column(db.String(255), nullable=True)
    before_value = db.Column(db.Text, nullable=True)
    after_value = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

