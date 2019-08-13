from sqlalchemy import Column, Integer, Text

from models.base_model import BaseModel, validatable
from validation.validators import IntegerMinValueValidator, StringUrlValidator


@validatable
class Link(BaseModel):
    __tablename__ = 'link'

    id = Column(Integer, primary_key=True)
    url = Column(Text, nullable=False)

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.url, [StringUrlValidator()])

    _default_fields = [
        "url"
    ]
