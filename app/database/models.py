from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.db_manager import Base

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, nullable=False)
    invoice_type = Column(String, nullable=False) # 'AP' or 'AR'
    counterparty_name = Column(String, nullable=False, index=True)
    counterparty_email = Column(String)
    counterparty_tax_id = Column(String)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    received_date = Column(Date)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    description = Column(Text)
    po_number = Column(String)
    status = Column(String, default="pending")
    source = Column(String, default="manual")
    source_filename = Column(String)
    source_path = Column(String)
    ocr_confidence = Column(Float, default=0.0)
    ocr_raw_text = Column(Text)
    fraud_score = Column(Float, default=0.0, index=True)
    is_duplicate = Column(Integer, default=0)
    duplicate_of_id = Column(Integer, ForeignKey("invoices.id"))
    requires_human_review = Column(Integer, default=0)
    human_review_notes = Column(Text)
    afis_transaction_id = Column(Integer)
    axis_classified = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    reconciliations = relationship("Reconciliation", back_populates="invoice")
    dunning_campaigns = relationship("DunningCampaign", back_populates="invoice")
    fraud_alerts = relationship("FraudAlert", back_populates="invoice")

class Reconciliation(Base):
    __tablename__ = "reconciliations"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    afis_transaction_id = Column(Integer, nullable=False)
    match_type = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    matched_amount = Column(Float, nullable=False)
    variance_amount = Column(Float, default=0.0)
    variance_reason = Column(Text)
    match_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    matched_by = Column(String, default="apex_agent")
    status = Column(String, default="pending_review")
    reviewed_by_human = Column(Integer, default=0)
    human_notes = Column(Text)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    invoice = relationship("Invoice", back_populates="reconciliations")

class DunningCampaign(Base):
    __tablename__ = "dunning_campaigns"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    campaign_stage = Column(Integer, nullable=False, default=1)
    days_overdue = Column(Integer, nullable=False, default=0)
    tone = Column(String, nullable=False)
    email_subject = Column(String)
    email_body = Column(Text)
    email_to = Column(String)
    email_sent = Column(Integer, default=0)
    email_sent_at = Column(DateTime)
    email_opened = Column(Integer, default=0)
    email_opened_at = Column(DateTime)
    response_received = Column(Integer, default=0)
    response_notes = Column(Text)
    next_action_date = Column(Date)
    status = Column(String, default="draft")
    generated_by = Column(String, default="apex_agent")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    invoice = relationship("Invoice", back_populates="dunning_campaigns")

class FraudAlert(Base):
    __tablename__ = "fraud_alerts"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    fraud_score = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    features_flagged = Column(Text)
    status = Column(String, default="open")
    investigated_by = Column(String)
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    invoice = relationship("Invoice", back_populates="fraud_alerts")

class DSOSnapshot(Base):
    __tablename__ = "dso_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(Date, nullable=False, unique=True)
    dso_days = Column(Float, nullable=False)
    ar_balance = Column(Float, nullable=False)
    revenue_30d = Column(Float, nullable=False)
    overdue_amount = Column(Float, default=0.0)
    overdue_count = Column(Integer, default=0)
    collection_rate = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Counterparty(Base):
    __tablename__ = "counterparties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    address = Column(Text)
    tax_id = Column(String, unique=True)
    payment_terms = Column(Integer, default=30)
    credit_limit = Column(Float, default=0.0)
    avg_payment_days = Column(Float, default=0.0)
    on_time_rate = Column(Float, default=1.0)
    total_invoiced = Column(Float, default=0.0)
    total_paid = Column(Float, default=0.0)
    fraud_flag = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ApexSetting(Base):
    __tablename__ = "apex_settings"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
