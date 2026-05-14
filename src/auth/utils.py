from passlib.context import CryptContext
from src.config import Config
from datetime import datetime, timedelta
import jwt
import uuid
import logging

password_context = CryptContext(schemes=["bcrypt"])
ACCESS_TOKEN_EXPIRY = 3600

def generate_password(password: str)->str:    
    return password_context.hash(password)

def verify_password(password: str, hash_passowrd: str)->bool:
    return password_context.verify(password, hash_passowrd)

def create_token_access(user_data: dict, expiry: timedelta = None, refresh: bool=False)-> str:
    payload={}
    
    payload["user"] = user_data
    
    payload["exp"] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    
    payload["jti"] = str(uuid.uuid4())
    
    payload["refresh"] = refresh
    
    token = jwt.encode(
        payload=payload,
        key = Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )
    
    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt = token,
            key = Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        
        return token_data
        
    except jwt.ExpiredSignatureError as e:
        logging.exception("Token expired")
        return None