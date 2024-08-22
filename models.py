from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class FormStructure(Base):
    __tablename__ = "form_structures"

    id = Column(Integer, primary_key=True, index=True)
    form_name = Column(String, index=True)
    fields = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True, index=True)
    form_structure_id = Column(Integer, ForeignKey('form_structures.id'))
    form_name = Column(String)  
    submitted_data = Column(JSON, nullable=False)
    form_structure = relationship("FormStructure", backref="submissions")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())