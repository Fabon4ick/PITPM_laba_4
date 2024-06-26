from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import IntegrityError
import datetime

# Создание объекта FastAPI
app = FastAPI()

# Настройка базы данных MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://isp_p_Shipitsyn:12345@77.91.86.135/isp_p_Shipitsyn"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Определение модели SQLAlchemy для вида товара
class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)


Base.metadata.create_all(bind=engine)


# Определение модели SQLAlchemy для модели
class Model(Base):
    __tablename__ = "model"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    price = Column(Float(2), index=True)
    product = relationship("Product")


Base.metadata.create_all(bind=engine)


# Определение модели SQLAlchemy для чека
class Receipt(Base):
    __tablename__ = "receipt"
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey('model.id'))
    receiptDate = Column(DateTime, index=True)
    quantity = Column(Integer, index=True)
    whoAccepted = Column(String(100), index=True)
    model = relationship("Model")


Base.metadata.create_all(bind=engine)


# Определение Pydantic модели для товара
class ProductCreate(BaseModel):
    name: str


class ProductResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# Определение Pydantic модели для модели
class ModelCreate(BaseModel):
    name: str
    product_id: int
    price: int


class ModelResponse(BaseModel):
    id: int
    name: str
    product_id: int
    price: float

    class Config:
        orm_mode = True


# Определение Pydantic модели для чека
class ReceiptCreate(BaseModel):
    model_id: int
    receiptDate: datetime.datetime
    quantity: int
    whoAccepted: str


class ReceiptResponse(BaseModel):
    id: int
    model_id: int
    receiptDate: datetime.datetime
    quantity: int
    whoAccepted: str

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/product/{id}", response_model=ProductResponse)
def read_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/product/", response_model=ProductResponse)
def create_product(name: str, db: Session = Depends(get_db)):
    new_product = Product(name=name)
    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Product already registered")


@app.delete("/product/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


@app.put("/product/{product_id}")
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    existing_product = db.query(Product).filter(Product.id == product_id).first()
    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_product.name = product.name
    db.commit()
    db.refresh(existing_product)

    return existing_product

@app.get("/model/{id}", response_model=ModelResponse)
def read_model(id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == id).first()
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@app.post("/model/", response_model=ModelResponse)
def create_model(name: str, product_id: int, price: float, db: Session = Depends(get_db)):
    new_model = Model(name=name, product_id=product_id, price=price)
    try:
        db.add(new_model)
        db.commit()
        db.refresh(new_model)
        return new_model
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Product already registered")


@app.delete("/model/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    db.delete(model)
    db.commit()
    return {"message": "Model deleted successfully"}


@app.put("/model/{model_id}")
def update_model(model_id: int, model: ModelCreate, db: Session = Depends(get_db)):
    existing_model = db.query(Model).filter(Model.id == model_id).first()
    if existing_model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    existing_model.name = model.name
    existing_model.product_id = model.product_id
    existing_model.price = model.price
    db.commit()
    db.refresh(existing_model)

    return existing_model


@app.get("/receipt/{id}", response_model=ReceiptResponse)
def read_receipt(id: int, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.id == id).first()
    if receipt is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return receipt


@app.post("/receipt/", response_model=ReceiptResponse)
def create_receipt(model_id: int, receiptDate: datetime.datetime, quantity: int, whoAccepted: str, db: Session = Depends(get_db)):
    new_receipt = Receipt(model_id=model_id, receiptDate=receiptDate, quantity=quantity, whoAccepted=whoAccepted)
    try:
        db.add(new_receipt)
        db.commit()
        db.refresh(new_receipt)
        return new_receipt
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Product already registered")


@app.delete("/receipt/{receipt_id}")
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    db.delete(receipt)
    db.commit()
    return {"message": "Receipt deleted successfully"}


@app.put("/receipt/{receipt_id}")
def update_receipt(receipt_id: int, receipt: ReceiptCreate, db: Session = Depends(get_db)):
    existing_receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if existing_receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")

    existing_receipt.model_id = receipt.model_id
    existing_receipt.receiptDate = receipt.receiptDate
    existing_receipt.quantity = receipt.quantity
    existing_receipt.whoAccepted = receipt.whoAccepted
    db.commit()
    db.refresh(existing_receipt)

    return existing_receipt