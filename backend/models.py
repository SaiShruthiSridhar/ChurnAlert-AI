from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(String, primary_key=True)
    name = Column(String)
    tenure = Column(Integer)
    monthly_charges = Column(Float)
    contract_type = Column(String)
    assigned_csm = Column(String)
    status = Column(String, default="Active")
    last_login_date = Column(DateTime)
    renewal_date = Column(DateTime)
    contract_value = Column(Float)
    
    # Week 5: Outcome fields
    intervention_date = Column(DateTime)
    outcome_date = Column(DateTime)
    was_successful = Column(Boolean) # True if renewed, False if churned

    risk_score = relationship("RiskScore", back_populates="account", uselist=False)
    usage_metrics = relationship("UsageMetric", back_populates="account")
    support_tickets = relationship("SupportTicket", back_populates="account")

class UsageMetric(Base):
    __tablename__ = 'usage_metrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, ForeignKey('accounts.id'))
    login_frequency = Column(Integer)
    feature_adoption_pct = Column(Float)
    session_duration_avg = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    account = relationship("Account", back_populates="usage_metrics")

class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, ForeignKey('accounts.id'))
    subject = Column(String)
    sentiment = Column(String)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    account = relationship("Account", back_populates="support_tickets")

class RiskScore(Base):
    __tablename__ = 'risk_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, ForeignKey('accounts.id'))
    score = Column(Float)
    tier = Column(String)
    reasons = Column(String)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    account = relationship("Account", back_populates="risk_score")

class RuleWeight(Base):
    __tablename__ = 'rule_weights'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String, unique=True)
    weight = Column(Float, default=1.0)
    last_adjusted = Column(DateTime, default=datetime.datetime.utcnow)

class RuleThreshold(Base):
    __tablename__ = 'rule_thresholds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String, unique=True, nullable=False)
    value = Column(Float, nullable=False)
    label = Column(String, nullable=False)
    description = Column(String, nullable=False)
    unit = Column(String, default='')
    min_value = Column(Float, default=0)
    max_value = Column(Float, default=100)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    company_name = Column(String, default='')
    role = Column(String, nullable=False)  # 'csm' or 'admin'
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
