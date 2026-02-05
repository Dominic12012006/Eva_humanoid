from datetime import timedelta,timezone,datetime
from jose import JWTError,jwt
from . import schemas

secret_key='09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
my_algo='HS256'
access_token=30

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=access_token)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,secret_key,algorithm=my_algo)
    return encoded_jwt

def verify_token(token1:str,credentials_exception):
    try:
        payload=jwt.decode(token1,secret_key,algorithms=[my_algo])
        email:str=payload.get("sub")
        if email is None :
            raise credentials_exception
        token_data=schemas.TokenData(email=email)
        return token_data
    except JWTError:
        raise credentials_exception