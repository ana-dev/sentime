from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from validation.validators import IntegerValidator, StringMaxLengthValidator, DatetimeValidator, EnumValidator
from models.enums import EmbeddingModelStatus
from models.assotiations import embedding_model_file
from models.base_model import BaseModel, validatable


@validatable
class EmbeddingModel(BaseModel):
    __tablename__ = 'embedding_model'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    info = Column(String(1000))
    updated_time = Column(DateTime, default=datetime.now)

    embedding_dim = Column(Integer)

    status = Column(Enum(EmbeddingModelStatus), default=EmbeddingModelStatus.created, nullable=False)

    embedding_method_id = Column(Integer, ForeignKey("embedding_method.id"))
    embedding_method = relationship("EmbeddingMethod", back_populates="embedding_models")

    embedding_params = relationship("EmbeddingMethodParamValue")

    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id"))
    vocabulary = relationship("Vocabulary")

    model_word_vectors = relationship("ModelWordVector")

    files = relationship("File", secondary=embedding_model_file)

    @classmethod
    def register_validators(cls):
        cls.__register_col_validators__(cls.id, [IntegerValidator()])
        cls.__register_col_validators__(cls.name, [StringMaxLengthValidator(100)])
        cls.__register_col_validators__(cls.info, [StringMaxLengthValidator(1000)])
        cls.__register_col_validators__(cls.updated_time, [DatetimeValidator()])
        cls.__register_col_validators__(cls.embedding_dim, [IntegerValidator()])
        cls.__register_col_validators__(cls.status, [EnumValidator(EmbeddingModelStatus)])

    _default_fields = [
        "name",
        "info",
        "updated_time",
        "embedding_dim",
        "embedding_method",
        "embedding_params",
        "vocabulary",
        "files",
        "status"
    ]
