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

class ResponseOut(ResponseBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class Questionresponse(BaseModel):
    answer:str