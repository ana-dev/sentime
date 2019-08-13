from sqlalchemy import Column, Integer, String, Enum, Index, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from models.assotiations import vocabulary_file
from models.enums import Language, Normalization, VocabularyStatus
from models.base_model import BaseModel, validatable
from validation.validators import StringMaxLengthValidator, IntegerValidator, EnumValidator, BooleanValidator, \
    DatetimeValidator


@validatable
class Vocabulary(BaseModel):
    __tablename__ = 'vocabulary'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    language = Column(Enum(Language), nullable=False)
    info = Column(String(1000))
    updated_time = Column(DateTime, default=datetime.now)

    lower_cased = Column(Boolean, nullable=False)
    normalization_method = Column(Enum(Normalization), nullable=False)
    punctuation_removed = Column(Boolean, nullable=False)

    words = relationship("Word", back_populates="vocabulary")

    files = relationship("File", secondary=vocabulary_file)

    status = Column(Enum(VocabularyStatus), default=VocabularyStatus.created, nullable=False)

    __table_args__ = (
        Index('name_and_language_unique', name, language, unique=True),
    )

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerValidator()])
        cls.__register_col_validators__(cls.name, [StringMaxLengthValidator(50)])
        cls.__register_col_validators__(cls.language, [EnumValidator(Language)])
        cls.__register_col_validators__(cls.info, [StringMaxLengthValidator(1000)])
        cls.__register_col_validators__(cls.updated_time, [DatetimeValidator()])
        cls.__register_col_validators__(cls.lower_cased, [BooleanValidator()])
        cls.__register_col_validators__(cls.normalization_method, [EnumValidator(Normalization)])
        cls.__register_col_validators__(cls.punctuation_removed, [BooleanValidator()])

    _default_fields = [
        "name",
        "language",
        "info",
        "updated_time",
        "lower_cased",
        "normalization_method",
        "punctuation_removed"
    ]
