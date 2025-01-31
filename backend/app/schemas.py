from pydantic import BaseModel
from typing import Optional, List

class DomainOut(BaseModel):
    id: int
    domain_name: str

    class Config:
        orm_mode = True

class PageTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
