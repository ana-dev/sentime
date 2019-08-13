from sqlalchemy import Column, Integer, Table, ForeignKey

from models.base_model import BaseModel

vocabulary_file = Table('vocabulary_file', BaseModel.metadata,
    Column('vocabulary_id', Integer, ForeignKey('vocabulary.id')),
    Column('file_id', Integer, ForeignKey('file.id'))
)

embedding_model_file = Table('embedding_model_file', BaseModel.metadata,
    Column('embedding_model_id', Integer, ForeignKey('embedding_model.id')),
    Column('file_id', Integer, ForeignKey('file.id'))
)

net_file = Table('net_file', BaseModel.metadata,
    Column('net_id', Integer, ForeignKey('net.id')),
    Column('file_id', Integer, ForeignKey('file.id'))
)

