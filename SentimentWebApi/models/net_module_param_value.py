from sqlalchemy import Column, Integer, String, Index, Float, ForeignKey
from sqlalchemy.orm import relationship

from validation.validators import IntegerMinValueValidator, FloatValidator
from models.base_model import BaseModel, validatable


@validatable
class NetModuleParamValue(BaseModel):
    __tablename__ = 'net_module_param_value'

    id = Column(Integer, primary_key=True)

    value = Column(Float(precision=5), nullable=False)

    net_module_param_id = Column(Integer, ForeignKey("net_module_param.id"))
    net_module_param = relationship("NetModuleParam")

    net_id = Column(Integer, ForeignKey("net.id"))

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.value, [FloatValidator()])

    _default_fields = [
        "value",
        "net_module_param"
    ]
