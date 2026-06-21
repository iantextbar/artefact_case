from datetime import datetime
import ast
import json
from typing import Optional, Callable

from pathlib import Path
import pandas as pd

from src.data_processing.models import Categories, Customers, OrderItems, Orders, Products, Promotions
from src.data_processing.schemas import CategoriesSchema, CustomersSchema, OrderItemsSchema, OrdersSchema, ProductsSchema, PromotionsSchema
from src.utils.storage import Db

# Get storage and set global variables
DB = Db()
ROOT_PATH = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT_PATH / "data" / "raw"

# --- Data preparation functions

def clean_and_validate_specs(spec_val: str) -> str:

    if pd.isna(spec_val) or not spec_val:
        return "{}"

    try:
        dic = ast.literal_eval(str(spec_val))
        return json.dumps(dic, ensure_ascii=False)
    except:
        return str(spec_val)

# --- Main data insertion function  
def insert_data_to_table(df: pd.DataFrame, model, schema):

    # Get list of dicts
    dict_list = df.to_dict(orient="records")

    objects_orm = []
    for reg in dict_list:
        try:

            # Validate data with pydantic
            validated = schema(**reg)

            # Put into expected model
            obj = model(**validated.model_dump())
            objects_orm.append(obj)

        except Exception as e:
            print(f'Error in validation for {reg}: {str(e)}')
            continue

    if objects_orm:
        with DB.get_session() as session:
            session.add_all(objects_orm)
        
        return {
            "status_code": 200,
            "records_inserted": len(objects_orm)
        }
    
    return {
        "status_code": 400,
        "error": "No objects found"
    }

def process_df_to_sql(df, model, schema, transformer_fnc: Optional[Callable] = None):

    DB.create_table(model)
    if transformer_fnc:
        df = transformer_fnc(df)
        df = df.where(df.notna(), None)

    result = insert_data_to_table(df, model, schema)

    if result['status_code'] == 200:
        print("Dataframe dimensions:", df.shape, "Inserted:", result['records_inserted'])
    else:
        print("ERROR")


# --- CSV specific cleaning functions
def prepare_products(df: pd.DataFrame):
    df['specs'] = df['specs'].apply(clean_and_validate_specs)
    return df

def prepare_orders(df: pd.DataFrame):
    # Add empty values as None
    df = df.astype(object).where(df.notna(), None)
    return df

def main():

    DB.drop_all_tables()

    # Read data
    categories = pd.read_csv(f"{DATA_PATH}/desafio_tecnico_ai_eng - categories.csv")
    customers = pd.read_csv(f"{DATA_PATH}/desafio_tecnico_ai_eng - customers.csv")
    order_items = pd.read_csv(f"{DATA_PATH}/desafio_tecnico_ai_eng - order_items.csv")
    orders = pd.read_csv(f"{DATA_PATH}/desafio_tecnico_ai_eng - orders.csv")
    products = pd.read_csv(f"{DATA_PATH}/desafio_tecnico_ai_eng - products.csv")
    promotions = pd.read_csv(f"{DATA_PATH}/desafio_tecnico_ai_eng - promotions.csv")

    # Process and insert to table
    print("Categories")
    process_df_to_sql(categories, Categories, CategoriesSchema)

    print("Customers")
    process_df_to_sql(customers, Customers, CustomersSchema)

    print("Order Items")
    process_df_to_sql(order_items, OrderItems, OrderItemsSchema)

    print("Orders")
    process_df_to_sql(orders, Orders, OrdersSchema, prepare_orders)

    print("Products")
    process_df_to_sql(products, Products, ProductsSchema, prepare_products)

    print("promotions")
    process_df_to_sql(promotions, Promotions, PromotionsSchema)

if __name__ == "__main__":
    main()
