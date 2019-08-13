from sqlalchemy import Column, Integer, String, ForeignKey

from models.base_model import BaseModel, validatable
from validation.validators import StringMaxLengthValidator, IntegerMinValueValidator


@validatable
class EpochConfusionMatrix(BaseModel):
    __tablename__ = 'epoch_confusion_matrix'

    id = Column(Integer, primary_key=True)

    epoch_id = Column(Integer, ForeignKey("epoch.id"))

    true_tag = Column(String(50), nullable=False)
    predicted_tag = Column(String(50), nullable=False)
    count = Column(Integer, nullable=False)

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.true_tag, [StringMaxLengthValidator(50)])
        cls.__register_col_validators__(cls.predicted_tag, [StringMaxLengthValidator(50)])
        cls.__register_col_validators__(cls.count, [IntegerMinValueValidator(0)])

    _default_fields = [
        "true_tag",
        "predicted_tag",
        "count"
    ]
