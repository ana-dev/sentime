from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from validation.validators import IntegerValidator, StringMaxLengthValidator, DatetimeValidator
from models.base_model import BaseModel, validatable


@validatable
class File(BaseModel):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)
    mimetype = Column(String(50), nullable=False)
    uploaded_time = Column(DateTime, default=datetime.now)

    path = Column(String(255), nullable=True)
    separator = Column(String(10), nullable=True)
    text_column = Column(Integer)
    tag_column = Column(Integer)
    positive_tag = Column(String(50))
    negative_tag = Column(String(50))

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerValidator()])
        cls.__register_col_validators__(cls.name, [StringMaxLengthValidator(100)])
        cls.__register_col_validators__(cls.mimetype, [StringMaxLengthValidator(50)])
        cls.__register_col_validators__(cls.uploaded_time, [DatetimeValidator()])
        cls.__register_col_validators__(cls.path, [StringMaxLengthValidator(255)])
        cls.__register_col_validators__(cls.separator, [StringMaxLengthValidator(10)])
        cls.__register_col_validators__(cls.text_column, [IntegerValidator()])
        cls.__register_col_validators__(cls.tag_column, [IntegerValidator()])
        cls.__register_col_validators__(cls.positive_tag, [StringMaxLengthValidator(50)])
        cls.__register_col_validators__(cls.negative_tag, [StringMaxLengthValidator(50)])

    _default_fields = [
        "name",
        "mimetype",
        "uploaded_time",
        "path",
        "separator",
        "text_column",
        "tag_column",
        "positive_tag",
        "negative_tag"
    ]
