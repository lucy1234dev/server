"""
Product API for Flower Shop.

Handles adding, listing, and saving product data in JSON format.

Author: Your Name
Date: 2025-06-19
"""

import os
import uuid
import json
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Constants
DATA_DIR = "data"
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
os.makedirs(DATA_DIR, exist_ok=True)


class ProductCreate(BaseModel):
    """Schema for creating a product."""
    name: str
    price: float
    categories: str
    page: str
    image: str


class Product(ProductCreate):
    """Schema for returning product with ID."""
    id: str


def load_products() -> List[Dict[str, Any]]:
    """
    Load products from the JSON file.

    Returns:
        List[Dict[str, Any]]: List of products.
    """
    if not os.path.exists(PRODUCTS_FILE):
        return []

    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_products(products: List[Dict[str, Any]]) -> None:
    """
    Save product list to JSON file.

    Args:
        products (List[Dict[str, Any]]): List of products to save.
    """
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as file:
        json.dump(products, file, indent=2)


@app.get("/products", response_model=List[Product])
def get_products():
    """
    Get all products.

    Returns:
        List[Product]: List of all products.
    """
    return load_products()


@app.post("/product", response_model=Product)
def add_product(product: ProductCreate):
    """
    Add a new product to the list.

    Args:
        product (ProductCreate): Product data.

    Returns:
        Product: The added product with ID.
    """
    if product.price <=0:
        raise HTTPException(status_code = 400, detail = "price must be greater than 0")

    products = load_products()

    new_product = {
        "id": str(uuid.uuid4()),
        "name": product.name,
        "price": product.price,
        "categories": product.categories,
        "page": product.page,
        "image": product.image
    }

    products.append(new_product)
    save_products(products)

    return new_product
