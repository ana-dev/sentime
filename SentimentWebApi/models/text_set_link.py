from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.base_model import BaseModel


class TextSetLink(BaseModel):
    __tablename__ = 'text_set_link'

    id = Column(Integer, primary_key=True)

    text_set_id = Column(Integer, ForeignKey('text_set.id'), nullable=False)
    link_id = Column(Integer, ForeignKey('link.id'), nullable=False)

    texts = relationship("LinkText", back_populates='text_set_link')

    link = relationship("Link")

    _default_fields = [
        "texts",
        "link"
    ]
