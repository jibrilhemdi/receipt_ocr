from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import tempfile
import traceback

from .db import Base, engine, SessionLocal
from . import models, schemas
from .ocr_service import extract_text_from_image
from .llm_service import parse_receipt_with_llm

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Receipt OCR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # you may later restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency - DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Existing test endpoint (keep it)
@app.post("/test-receipt", response_model=schemas.Receipt)
def create_test_receipt(db: Session = Depends(get_db)):
    dummy_receipt = models.Receipt(
        merchant="Test Store",
        total=10.0,
        currency="USD",
        raw_text="Dummy raw text",
        extra_data={"note": "created from /test-receipt endpoint"}
    )
    db.add(dummy_receipt)
    db.commit()
    db.refresh(dummy_receipt)
    return dummy_receipt



@app.post("/receipts", response_model=schemas.Receipt)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    suffix = os.path.splitext(file.filename)[1] or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        print(f"[DEBUG] Saved upload to: {tmp_path}")

        # 1) OCR
        try:
            ocr_text = extract_text_from_image(tmp_path)
            print("[DEBUG] OCR text preview:", ocr_text[:300].replace("\n", "\\n"))
        except Exception as e:
            print("[ERROR] OCR failed:")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"OCR error: {e}")

        if not ocr_text.strip():
            raise HTTPException(status_code=422, detail="OCR failed to extract text")

        # 2) LLM
        try:
            parsed = parse_receipt_with_llm(ocr_text)
            print("[DEBUG] LLM parsed dict:", parsed)
        except Exception as e:
            print("[ERROR] LLM parsing failed:")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"LLM error: {e}")

        # 3) Map to schemas
        items_data = parsed.get("items") or []
        receipt_create = schemas.ReceiptCreate(
            merchant=parsed.get("merchant"),
            purchase_date=parsed.get("purchase_date"),
            total=parsed.get("total"),
            currency=parsed.get("currency") or "USD",
            raw_text=ocr_text,
            extra_data=parsed.get("extra_data"),
            items=[
                schemas.LineItemCreate(**item)
                for item in items_data
                if "name" in item
            ]
        )

        # 4) Save to DB
        db_receipt = models.Receipt(
            merchant=receipt_create.merchant,
            purchase_date=receipt_create.purchase_date,
            total=receipt_create.total,
            currency=receipt_create.currency,
            raw_text=receipt_create.raw_text,
            extra_data=receipt_create.extra_data,
        )
        db.add(db_receipt)
        db.flush()

        for item in receipt_create.items:
            db_item = models.LineItem(
                receipt_id=db_receipt.id,
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.line_total,
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_receipt)

        return db_receipt

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/receipts", response_model=List[schemas.Receipt])
def list_receipts(db: Session = Depends(get_db)):
    receipts = db.query(models.Receipt).all()
    return receipts


@app.get("/receipts/{receipt_id}", response_model=schemas.Receipt)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = db.query(models.Receipt).filter(models.Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


@app.delete("/receipts/{receipt_id}")
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = db.query(models.Receipt).filter(models.Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    db.delete(receipt)
    db.commit()
    return {"deleted": True}