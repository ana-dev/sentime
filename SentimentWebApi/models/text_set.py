from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, validatable
from validation.validators import IntegerMinValueValidator, StringMaxLengthValidator


@validatable
class TextSet(BaseModel):
    __tablename__ = 'text_set'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)

    files = relationship("TextSetFile")
    links = relationship("TextSetLink")

    net = relationship("Net")
    net_id = Column(Integer, ForeignKey("net.id"))

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.name, [StringMaxLengthValidator(256)])

    _default_fields = [
        "name",
        "files",
        "links",
        "net"
    ]
