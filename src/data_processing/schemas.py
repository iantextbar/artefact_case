from pydantic import BaseModel
from typing import Literal, Optional

class CategoriesSchema(BaseModel):
    
    category_id: int
    name: str
    description: str

class CustomersSchema(BaseModel):

    customer_id: int
    name: str
    phone: str
    email: str
    city: str

class OrderItemsSchema(BaseModel):

    order_id: int
    quantity: int
    product_id: int

class OrdersSchema(BaseModel):

    order_id: int
    customer_id: int
    order_date: str
    status: Literal['delivered', 'shipped', 'confirmed', 'pending', 'cancelled']
    total_brl: float
    payment_method: str
    tracking_code: Optional[str] = None
    estimated_delivery: Optional[str] = None
    notes: Optional[str] = None

class ProductsSchema(BaseModel):

    product_id: int
    price_brl: float
    name: str
    category_id: int
    description: str
    status: str
    stock_quantity: int
    specs: str
    created_at: str

class PromotionsSchema(BaseModel):
    
    promotion_id: int
    product_id: int
    discount_percent: int
    description: str
    is_active: bool
