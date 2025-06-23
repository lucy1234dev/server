from fastapi import FastAPI
from signup import router as signup_router
from product import router as product_router

app = FastAPI()

# Root route to avoid "Not Found" on home
@app.get("/")
def read_root():
    """read root of the application"""

    return {"message": "🌸 Welcome to the Flower Shop API!"}

# Include feature-specific routers
app.include_router(signup_router)
app.include_router(product_router)
