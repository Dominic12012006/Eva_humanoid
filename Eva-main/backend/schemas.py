from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
class ResponseBase(BaseModel):
    type: str = Field(..., description="text | map | image | status")
    data: str
    map_data:Optional[Dict[str , float]]=None
    llm_name: Optional[str] = 'Eva'
    confidence: Optional[float] = None

class ResponseCreate(ResponseBase):
    pass
class Show_questions(BaseModel):
    id:int
    question:str

class Show_answer(BaseModel):
    id:int
    answer:str
class Show_image(BaseModel):
    id:int
    image:str
class ResponseOut(ResponseBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class Questionresponse(BaseModel):
    answer:str
    lang:str

class Admin(BaseModel):
    email:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str
class TokenData(BaseModel):
    email:Optional[str]=None

