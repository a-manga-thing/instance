from . import Base
from sqlalchemy import Column, Integer, Enum, Boolean, Text, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, selectinload
import enum

from .creators import Author, Artist

class Types(enum.Enum):
    Manga = 1
    Webtoon = 2

class PubStatuses(enum.Enum):
    Ongoing = 1
    Axed = 2
    Completed = 3

class Title(Base):
    __tablename__ = "titles"
    id = Column(Integer, autoincrement=True, primary_key=True)
    manga_id = Column(Integer, ForeignKey("manga.id"))
    title = Column(Text)

class Genre(Base):
    __tablename__ = "genre"

    id = Column(Integer, primary_key=True)
    name = Column(Text)

MangaGenre = Table('mangagenre', Base.metadata,
    Column("manga_id", Integer, ForeignKey("manga.id")),
    Column("genre_id", Integer, ForeignKey("genre.id"))
)

class Manga(Base):
    __tablename__ = "manga"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_type = Column(Enum(Types))
    country_of_origin = Column(Text)
    publication_status = Column(Enum(PubStatuses))
    scanlation_status = Column(Boolean)
    mal_id = Column(Integer)
    anilist_id = Column(Integer)
    mu_id = Column(Integer)
    last_updated = Column(DateTime)

    genres = relationship("Genre", secondary=MangaGenre)
    authors = relationship("Person", secondary=Author)
    artists = relationship("Person", secondary=Artist)
    titles = relationship("Title")

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.content_type.name,
            "titles": [i.title for i in self.titles],
            "artists": [i.name for i in self.artists],
            "authors": [i.name for i in self.authors],
            "genres": [i.name for i in self.genres],
            "country_of_origin": self.country_of_origin,
            "publication_status": self.publication_status.name,
            "scanlation_status": self.scanlation_status,
            "mal_id": self.mal_id,
            "anilist_id": self.anilist_id,
            "mangaupdates_id": self.mu_id,
            "last_updated": int(self.last_updated.timestamp()) if self.last_updated else 0
        }

    def __str__(self):
        return self.titles[0].title

Manga._query_options = [selectinload(i) for i in (Manga.artists, Manga.authors, Manga.titles, Manga.genres)]
#^ The eager loader is needed else it throws an asyncio error