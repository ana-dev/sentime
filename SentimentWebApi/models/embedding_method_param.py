from sqlalchemy import Column, Integer, String, Index, ForeignKey

from models.base_model import BaseModel, validatable

from validation.validators import IntegerValidator, StringMaxLengthValidator, AllowedValuesValidator


@validatable
class EmbeddingMethodParam(BaseModel):
    __tablename__ = 'embedding_method_param'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)
    display_name = Column(String(100), nullable=False)

    embedding_method_id = Column(Integer, ForeignKey("embedding_method.id"))

    __table_args__ = (
        Index('embedding_method_id_and_name_unique', embedding_method_id, name, unique=True),
    )

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerValidator()])
        cls.__register_col_validators__(cls.name, [StringMaxLengthValidator(50)])
        cls.__register_col_validators__(cls.type, [AllowedValuesValidator(['str', 'int', 'float'])])
        cls.__register_col_validators__(cls.display_name, [StringMaxLengthValidator(100)])

    _default_fields = [
        "name",
        "type",
        "display_name"
    ]
