from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str          
    question: str            
    top_k: int = 5         


class ChatResponse(BaseModel):
    session_id: str
    answer: str             
    sources: list[str]       
    booking: Optional[dict] = None   