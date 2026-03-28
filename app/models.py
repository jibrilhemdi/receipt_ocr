from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    merchant = Column(String, index=True, nullable=True)
    total = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    purchase_date = Column(DateTime, nullable=True)
    raw_text = Column(String, nullable=False)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship(
        "LineItem",
        back_populates="receipt",
        cascade="all, delete-orphan"
    )

class LineItem(Base):
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=True)
    line_total = Column(Float, nullable=True)

    receipt = relationship("Receipt", back_populates="items")