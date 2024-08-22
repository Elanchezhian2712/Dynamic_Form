from pydantic import BaseModel
from typing import List

class FormField(BaseModel):
    related_name: str  
    value: str 

class FormData(BaseModel):
    form_name: str
    fields: List[FormField] 
    
class FormSubmissionData(BaseModel):
    form_structure_id: int
    submitted_data: dict
    
    class Config:
        orm_mode = True