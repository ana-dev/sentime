from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, validatable

from validation.validators import IntegerValidator, FloatValidator


@validatable
class EmbeddingMethodParamValue(BaseModel):
    __tablename__ = 'embedding_method_param_value'

    id = Column(Integer, primary_key=True)

    value = Column(Float(precision=5), nullable=False)

    embedding_method_param_id = Column(Integer, ForeignKey("embedding_method_param.id"))
    embedding_method_param = relationship("EmbeddingMethodParam")

    embedding_model_id = Column(Integer, ForeignKey("embedding_model.id"))

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerValidator()])
        cls.__register_col_validators__(cls.value, [FloatValidator()])

    _default_fields = [
        "value",
        "embedding_method_param"
    ]
