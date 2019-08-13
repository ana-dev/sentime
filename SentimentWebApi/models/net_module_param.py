from sqlalchemy import Column, Integer, String, Index, ForeignKey

from validation.validators import IntegerMinValueValidator, StringMaxLengthValidator, AllowedValuesValidator
from models.base_model import BaseModel, validatable


@validatable
class NetModuleParam(BaseModel):
    __tablename__ = 'net_module_param'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)
    display_name = Column(String(100), nullable=False)

    net_module_id = Column(Integer, ForeignKey("net_module.id"))

    __table_args__ = (
        Index('net_module_id_and_name_unique', net_module_id, name, unique=True),
    )

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.name, [StringMaxLengthValidator(50)])
        cls.__register_col_validators__(cls.type, [AllowedValuesValidator(['float', 'str', 'int'])])
        cls.__register_col_validators__(cls.display_name, [StringMaxLengthValidator(100)])

    _default_fields = [
        "name",
        "type",
        "display_name"
    ]
