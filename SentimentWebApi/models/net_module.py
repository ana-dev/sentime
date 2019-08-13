from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from validation.validators import IntegerMinValueValidator, StringMaxLengthValidator, DatetimeValidator
from models.base_model import BaseModel, validatable


@validatable
class NetModule(BaseModel):
    __tablename__ = 'net_module'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    info = Column(String(1000))
    updated_time = Column(DateTime, default=datetime.now)

    plugin_path = Column(String(255), nullable=False, unique=True)

    net_module_params = relationship("NetModuleParam")

    nets = relationship("Net", back_populates="net_module")

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.name, [StringMaxLengthValidator(100)])
        cls.__register_col_validators__(cls.info, [StringMaxLengthValidator(1000)])
        cls.__register_col_validators__(cls.updated_time, [DatetimeValidator()])
        cls.__register_col_validators__(cls.plugin_path, [StringMaxLengthValidator(255)])

    _default_fields = [
        "name",
        "info",
        "updated_time",
        "plugin_path",
        "net_module_params"
    ]
