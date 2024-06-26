from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
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
