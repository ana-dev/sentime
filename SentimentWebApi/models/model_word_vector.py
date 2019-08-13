from sqlalchemy import Column, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from validation.validators import IntegerMinValueValidator, StringValidator, FloatValidator
from models.base_model import BaseModel, validatable


@validatable
class ModelWordVector(BaseModel):
    __tablename__ = 'model_word_vector'

    id = Column(Integer, primary_key=True)

    vector = Column(Text, nullable=False)
    index = Column(Integer, nullable=False)

    x = Column(Float, nullable=True)
    y = Column(Float, nullable=True)

    word_id = Column(Integer, ForeignKey("word.id"))
    word = relationship("Word")

    embedding_model_id = Column(Integer, ForeignKey("embedding_model.id"))

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.vector, [StringValidator()])
        cls.__register_col_validators__(cls.index, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.x, [FloatValidator()])
        cls.__register_col_validators__(cls.y, [FloatValidator()])

    _default_fields = [
        "vector",
        "index",
        "x",
        "y",
        "word"
    ]
