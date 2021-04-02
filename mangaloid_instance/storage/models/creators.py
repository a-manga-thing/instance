from . import Base
from sqlalchemy import Column, Integer, Text, ForeignKey, Table
from sqlalchemy.orm import relationship

class Person(Base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True)
    name = Column(Text)

Author = Table('authors', Base.metadata,
    Column("manga_id", Integer, ForeignKey("manga.id")),
    Column("person_id", Integer, ForeignKey("person.id"))
)

Artist = Table('artists', Base.metadata,
    Column("manga_id", Integer, ForeignKey("manga.id")),
    Column("person_id", Integer, ForeignKey("person.id"))
)