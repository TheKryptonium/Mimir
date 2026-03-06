from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"])

def generate_password(password: str)->str:    
    return password_context.hash(password)

def verify_password(password: str, hash_passowrd: str)->bool:
    return password_context.verify(password, hash_passowrd)