from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from models.assotiations import net_file
from models.enums import NetStatus
from validation.validators import IntegerMinValueValidator, StringMaxLengthValidator, DatetimeValidator, EnumValidator
from models.base_model import BaseModel, validatable


@validatable
class Net(BaseModel):
    __tablename__ = 'net'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    info = Column(String(1000))
    updated_time = Column(DateTime, default=datetime.now)
    net_file_path = Column(String(255), nullable=True, unique=True)
    status = Column(Enum(NetStatus), default=NetStatus.created, nullable=False)

    net_module_id = Column(Integer, ForeignKey("net_module.id"))
    net_module = relationship("NetModule", back_populates="nets")

    net_module_param_values = relationship("NetModuleParamValue")

    embedding_model_id = Column(Integer, ForeignKey("embedding_model.id"))
    embedding_model = relationship("EmbeddingModel")

    files = relationship("File", secondary=net_file)

    epochs = relationship("Epoch")

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.name, [StringMaxLengthValidator(100)])
        cls.__register_col_validators__(cls.info, [StringMaxLengthValidator(100)])
        cls.__register_col_validators__(cls.updated_time, [DatetimeValidator()])
        cls.__register_col_validators__(cls.net_file_path, [StringMaxLengthValidator(255)])
        cls.__register_col_validators__(cls.status, [EnumValidator(NetStatus)])

    _default_fields = [
        "name",
        "info",
        "updated_time",
        "net_module",
        "net_module_param_values",
        "embedding_model",
        "net_file_path",
        "files",
        "status",
        "epochs"
    ]
