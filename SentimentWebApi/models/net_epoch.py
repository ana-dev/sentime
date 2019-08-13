from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from validation.validators import IntegerMinValueValidator, StringMaxLengthValidator, FloatValidator
from models.base_model import BaseModel, validatable


@validatable
class Epoch(BaseModel):
    __tablename__ = 'epoch'

    id = Column(Integer, primary_key=True)
    order_number = Column(Integer, nullable=False)
    epoch_file_path = Column(String(255), nullable=True, unique=True)
    training_time = Column(Integer, nullable=True)
    train_accurancy = Column(Float, nullable=True)
    train_loss = Column(Float, nullable=True)
    test_accurancy = Column(Float, nullable=True)
    test_loss = Column(Float, nullable=True)

    net_id = Column(Integer, ForeignKey("net.id"))

    epoch_confusion_matrix = relationship("EpochConfusionMatrix")

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.order_number, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.epoch_file_path, [StringMaxLengthValidator(255)])
        cls.__register_col_validators__(cls.training_time, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.train_accurancy, [FloatValidator()])
        cls.__register_col_validators__(cls.train_loss, [FloatValidator()])
        cls.__register_col_validators__(cls.test_accurancy, [FloatValidator()])
        cls.__register_col_validators__(cls.test_loss, [FloatValidator()])

    _default_fields = [
        "order_number",
        "epoch_file_path",
        "epoch_confusion_matrix",
        "training_time",
        "train_accurancy",
        "train_loss",
        "test_accurancy",
        "test_loss"
    ]
