from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Boolean, Text, ForeignKey, Integer
from typing import Optional, List

from src.data_processing.base import Base

class Categories(Base):
    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Relations
    products: Mapped[List["Products"]] = relationship("Products", back_populates="category")


class Customers(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relations
    orders: Mapped[List["Orders"]] = relationship("Orders", back_populates="customer")


class OrderItems(Base):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relations
    order: Mapped["Orders"] = relationship("Orders", back_populates="items")
    product: Mapped["Products"] = relationship("Products")


class Orders(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), nullable=False)
    
    order_date: Mapped[str] = mapped_column(String(50), nullable=False) 
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    total_brl: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    
    tracking_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estimated_delivery: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relations
    customer: Mapped["Customers"] = relationship("Customers", back_populates="orders")
    items: Mapped[List["OrderItems"]] = relationship("OrderItems", back_populates="order")


class Products(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    price_brl: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    
    specs: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relations
    category: Mapped["Categories"] = relationship("Categories", back_populates="products")
    promotions: Mapped[List["Promotions"]] = relationship("Promotions", back_populates="product")


class Promotions(Base):
    __tablename__ = "promotions"

    promotion_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(150), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relations
    product: Mapped["Products"] = relationship("Products", back_populates="promotions")
