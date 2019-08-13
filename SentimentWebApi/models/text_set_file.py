from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.base_model import BaseModel


class TextSetFile(BaseModel):
    __tablename__ = 'text_set_file'

    id = Column(Integer, primary_key=True)

    text_set_id = Column(Integer, ForeignKey('text_set.id'), nullable=False)
    file_id = Column(Integer, ForeignKey('file.id'), nullable=False)

    texts = relationship("FileText", back_populates='text_set_file')

    file = relationship("File")

    _default_fields = [
        "texts",
        "file"
    ]
