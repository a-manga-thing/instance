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

class ScanlatorGroup(Base):
    __tablename__ = "scanlators"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    website = Column(Text)

    def to_dict(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "website" : self.website
        }

Scanlator = Table("scanlations", Base.metadata,
    Column("chapter_id", Integer, ForeignKey("chapters.id")),
    Column("scanlator_id", Integer, ForeignKey("scanlators.id"))
)