import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from .database import Base


class Deviation(Base):
    __tablename__ = "deviations"

    id = Column(Integer, primary_key=True, index=True)
    deviation_id = Column(String(32), unique=True, index=True)  # e.g. DEV-2026-0001
    title = Column(String(255), default="")
    description = Column(Text, default="")
    date_observed = Column(String(32), default="")
    observed_by = Column(String(128), default="")
    department = Column(String(128), default="")
    product = Column(String(128), default="")
    batch_no = Column(String(64), default="")
    stage = Column(String(128), default="")
    equipment = Column(String(128), default="")
    specification_limit = Column(String(255), default="")
    observed_value = Column(String(255), default="")
    deviation_type = Column(String(64), default="Process")
    severity = Column(String(32), default="Minor")
    impact_assessment = Column(Text, default="")
    probable_cause = Column(Text, default="")
    immediate_action = Column(Text, default="")
    capa_required = Column(Boolean, default=False)
    status = Column(String(32), default="Logged")
    ai_reason = Column(Text, default="")
    ai_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
