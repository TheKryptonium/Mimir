from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status
from .utils import decode_token

class TokenBearer(HTTPBearer):
    
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)
        
    async def __call__(self, request: Request)->HTTPAuthorizationCredentials|None:
        creds = await super().__call__(request)
        
        token = creds.credentials
        
        if not self.validate_token(token):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN, 
                detail="Provide an access token"
                )
        
        if token['refresh']:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Provide an access token"
            )
                
        return creds
    
    def validate_token(self, token: str)-> bool:
        token_data = decode_token(token)
        
        return True if token_data is not None else False
    
    def verify_token(self, token_data: dict)-> dict:
        raise NotImplementedError("Please override this method in the subclass")
    

class AccessTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict)-> bool:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Provide an access token"
            )
            
class RefreshTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict)-> bool:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Provide a refresh token"
            )    