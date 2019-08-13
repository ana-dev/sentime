from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship

from validation.validators import IntegerMinValueValidator, StringValidator, FloatValidator
from models.base_model import BaseModel, validatable


@validatable
class Text(BaseModel):
    __tablename__ = 'text'

    id = Column(Integer, primary_key=True)
    text_type = Column(String(50))

    text = Column(Text, nullable=False)
    negative_probability = Column(Float, nullable=False)
    positive_probability = Column(Float, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'text',
        'polymorphic_on': text_type
    }

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.text, [StringValidator()])
        cls.__register_col_validators__(cls.negative_probability, [FloatValidator()])
        cls.__register_col_validators__(cls.positive_probability, [FloatValidator()])

    _default_fields = [
        "text",
        "negative_probability",
        "positive_probability"
    ]


@validatable
class FileText(Text):
    __tablename__ = 'file_text'

    id = Column(Integer, ForeignKey('text.id'), primary_key=True)

    text_set_file_id = Column(Integer, ForeignKey('text_set_file.id'), nullable=False)
    text_set_file = relationship("TextSetFile", back_populates='texts')

    __mapper_args__ = {
        'polymorphic_identity': 'file_text',
    }


@validatable
class LinkText(Text):
    __tablename__ = 'link_text'

    id = Column(Integer, ForeignKey('text.id'), primary_key=True)

    text_set_link_id = Column(Integer, ForeignKey('text_set_link.id'), nullable=False)
    text_set_link = relationship("TextSetLink", back_populates='texts')

    id_from_link = Column(Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'link_text',
    }
