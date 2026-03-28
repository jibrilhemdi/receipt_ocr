from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class LineItemBase(BaseModel):
    name: str
    quantity: float = 1.0
    unit_price: Optional[float] = None
    line_total: Optional[float] = None

class LineItemCreate(LineItemBase):
    pass

class LineItem(LineItemBase):
    id: int

    class Config:
        orm_mode = True

class ReceiptBase(BaseModel):
    merchant: Optional[str] = None
    total: Optional[float] = None
    currency: Optional[str] = "USD"
    purchase_date: Optional[datetime] = None
    raw_text: str
    extra_data: Optional[dict] = None

class ReceiptCreate(ReceiptBase):
    items: List[LineItemCreate] = []

class Receipt(ReceiptBase):
    id: int
    created_at: datetime
    items: List[LineItem] = []

    class Config:
        orm_mode = True