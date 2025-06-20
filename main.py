# main.py
from fastapi import FastAPI
from signup import app as signup_app
from product import app as product_app

app = FastAPI()

# Mount sub-apps
app.mount("/signup", signup_app)
app.mount("/product", product_app)
