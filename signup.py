"""
Flower Shop Signup API using FastAPI.

This module provides endpoints to register new users, verify OTPs,
resend OTPs after 5 minutes, and list users. All data is stored in local
JSON files and OTPs are printed to the console.

Author: Your Name
Date: 2025-06-18
"""

import os
import re
import json
import time
import uuid
import random
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# File paths
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
OTPS_FILE = os.path.join(DATA_DIR, "otps.json")
os.makedirs(DATA_DIR, exist_ok=True)


class UserCreate(BaseModel):
    """Schema for creating a user."""
    name: str
    email: str
    password: str


class OTPVerify(BaseModel):
    """Schema for verifying an OTP."""
    email: str
    otp: str


class ResendRequest(BaseModel):
    """Schema for requesting OTP resend."""
    email: str

class UserLogin(BaseModel):
    """Schema for user Login."""
    email:str
    password:str


def load_data(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data from a file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        Dict[str, Any]: Loaded JSON data.
    """
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def save_data(file_path: str, data: Dict[str, Any]) -> None:
    """
    Save data to a JSON file.

    Args:
        file_path (str): Path to the file.
        data (Dict[str, Any]): Data to save.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def is_valid_email(email: str) -> bool:
    """
    Validate an email address.

    Args:
        email (str): Email to validate.

    Returns:
        bool: True if valid, else False.
    """
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))


def is_strong_password(password: str) -> bool:
    """
    Check password strength.

    Args:
        password (str): Password to check.

    Returns:
        bool: True if strong, else False.
    """
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
    )


def generate_otp() -> str:
    """
    Generate a 6-digit OTP.

    Returns:
        str: The generated OTP.
    """
    return ''.join(random.choices("0123456789", k=6))


@app.post("/signup")
def signup(user: UserCreate):
    """
    Register a new user and send OTP to console.

    Args:
        user (UserCreate): User signup details.

    Returns:
        dict: Success message.
    """
    users = load_data(USERS_FILE)
    otps = load_data(OTPS_FILE)

    if user.email in users:
        raise HTTPException(status_code=409, detail="User already exists.")

    if not is_valid_email(user.email):
        raise HTTPException(status_code=400, detail="Invalid email.")

    if not is_strong_password(user.password):
        raise HTTPException(status_code=400, detail="Weak password.")

    users[user.email] = {
        "id": str(uuid.uuid4()),
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "verified": False
    }
    save_data(USERS_FILE, users)

    otp = generate_otp()
    otps[user.email] = {
        "otp": otp,
        "timestamp": time.time()
    }
    save_data(OTPS_FILE, otps)

    print(f"[OTP] Your OTP for {user.email} is: {otp}")
    return {"message": "User registered. OTP sent to console."}


@app.post("/verify-otp")
def verify_otp(data: OTPVerify):
    """
    Verify user's OTP.

    Args:
        data (OTPVerify): Email and OTP.

    Returns:
        dict: Verification status.
    """
    otps = load_data(OTPS_FILE)

    if data.email not in otps:
        raise HTTPException(status_code=404, detail="No OTP found for this email.")

    if otps[data.email]["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    del otps[data.email]
    save_data(OTPS_FILE, otps)

    users = load_data(USERS_FILE)
    if data.email in users:
        users[data.email]["verified"] = True
        save_data(USERS_FILE, users)

    return {"message": "OTP verified successfully. User is now verified."}


@app.post("/resend-otp")
def resend_otp(data: ResendRequest):
    """
    Resend OTP after 5 minutes.

    Args:
        data (ResendRequest): Email requesting resend.

    Returns:
        dict: Resend status.
    """
    otps = load_data(OTPS_FILE)

    if data.email not in otps:
        raise HTTPException(status_code=404, detail="No signup found for this email.")

    elapsed = time.time() - otps[data.email]["timestamp"]
    if elapsed < 300:
        remaining = int(300 - elapsed)
        raise HTTPException(
            status_code=403,
            detail=f"Wait {remaining} seconds before resending OTP."
        )

    otp = generate_otp()
    otps[data.email] = {
        "otp": otp,
        "timestamp": time.time()
    }
    save_data(OTPS_FILE, otps)

    print(f"[OTP] Resent OTP for {data.email}: {otp}")
    return {"message": "OTP resent. Check console."}

@app.post("/login")
def login(data:UserLogin):
    """
    Login aregistered user.

    Args:
        data (UserLogin): Email and password.

    Raises:
        dict: Login status and message
    """


    users = load_data(USERS_FILE)


    user = users.get(data.email)
    if not user:
        raise HTTPException(status_code = 404, detail="user not found.")

    if not user.get("verified"):
        raise HTTPException(
            status_code = 404,
            detail = "Email not verified. Please verify OTP first."
            )

    if user["password"] !=data.password:
        raise HTTPException(status_code = 404, detail="incorrect password")
    return{"message": f"Login successful. welcome {user['name']}!"}


@app.get("/users")
def list_users():
    """
    Get all registered users.

    Returns:
        list: List of user data.
    """
    users = load_data(USERS_FILE)
    return list(users.values())


@app.get("/verified-users")
def get_verified_users():
    """
    List all users who are verified.

    Returns:
        list: Verified users.
    """
    users = load_data(USERS_FILE)
    return [u for u in users.values() if u.get("verified") is True]


@app.get("/")
def home():
    """
    API root.

    Returns:
        dict: Welcome message.
    """
    return {"message": "🌼 Welcome to Flower Shop Signup API 🌼"}
