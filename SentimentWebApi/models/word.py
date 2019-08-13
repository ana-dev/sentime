from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship

from validation.validators import IntegerValidator, StringMaxLengthValidator, IntegerMinValueValidator
from models.base_model import BaseModel, validatable


@validatable
class Word(BaseModel):
    __tablename__ = 'word'

    id = Column(Integer, primary_key=True)
    token = Column(String(100, collation="utf8mb4_bin"), nullable=False, index=True)
    token_id = Column(Integer, nullable=False, index=True)
    count = Column(Integer, nullable=False)
    vocabulary_id = Column(Integer, ForeignKey('vocabulary.id', ondelete='cascade'))
    vocabulary = relationship("Vocabulary", back_populates="words")

    __table_args__ = (
        Index('vocabulary_id_and_token_unique', vocabulary_id, token, unique=True),
    )

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerValidator()])
        cls.__register_col_validators__(cls.token, [StringMaxLengthValidator(100)])
        cls.__register_col_validators__(cls.token_id, [IntegerMinValueValidator(0)])
        cls.__register_col_validators__(cls.count, [IntegerMinValueValidator(0)])

    _default_fields = [
        "token",
        "count"
    ]
