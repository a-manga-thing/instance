from . import Base
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from datetime import datetime

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    manga_id = Column(Integer, ForeignKey("manga.id"))
    chapter_no = Column(Integer)
    chapter_postfix = Column(Text)
    ordinal = Column(Integer)
    page_count = Column(Integer)
    title = Column(Text)
    version = Column(Integer)
    language_id = Column(Text)
    group_id = Column(Integer)
    date_added = Column(DateTime)
    ipfs_link = Column(Text)

    def to_dict(self):
        return {
            "id" : self.id,
            "manga_id" : self.manga_id,
            "chapter_no" : self.chapter_no,
            "chapter_postfix" : self.chapter_postfix,
            "ordinal" : self.ordinal,
            "title" : self.title,
            "page_count" : self.page_count,
            "version" : self.version,
            "language_id" : self.language_id,
            "group_id" : self.group_id,
            "date_added" : int(self.date_added.timestamp()),
            "ipfs_link" : self.ipfs_link
        }