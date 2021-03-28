from .queries import QUERIES, DATABASE_CREATION
from models import manga, chapter
from asyncio import get_event_loop
from aiosqlite import Row, connect
from aiohttp.web import HTTPNotFound

class NotInitalized(RuntimeError):
    pass

class MangaNotFound(HTTPNotFound):
    def __init__(self, manga_id):
        super().__init__(text="Could not find manga with ID {}".format(manga_id))

class ChapterNotFound(HTTPNotFound):
    def __init__(self, manga_id, chapter):
        if chapter.is_integer():
            chapter = int(chapter)
        super().__init__(text="Could not find chapter {} of manga {}".format(chapter, manga_id))

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.db = None
    
    async def init(self):
        self.db = await connect(self.db_path)
        self.db.row_factory = Row
        async with self.db.cursor() as cursor:
            for q in DATABASE_CREATION:
                await cursor.execute(q)
            await self.db.commit()
    
    async def get_manga_by_id(self, query_id) -> manga.Manga:
        """Fetches a manga from the database by ID. Will raise MangaNotFound if not found"""
        if not self.db:
            raise NotInitalized()
        async with self.db.cursor() as cursor:
            res = await (await cursor.execute(QUERIES["MANGA_BY_ID"], (query_id,))).fetchall()
            if not res:
                raise MangaNotFound(query_id)
            creators = [i['creator_name'] for i in res]
            return manga.Manga(res[0], creators=creators)

    async def search_by_title(self, title) -> list:
        """Searches a manga based on title (any version). Will return an empty list of nothing is found"""
        if not self.db:
            raise NotInitalized()
        async with self.db.cursor() as cursor:
            res = await (await cursor.execute(QUERIES["TITLE_SEARCH"], ('%'+title+'%',))).fetchall()
            r = {}
            for row in res:
                if row['manga_id'] in r:
                    r[row['manga_id']].creators.append(row['creator_name'])
                else:
                    r[row['manga_id']] = manga.Manga(row)
            return list(r.values())

    async def search_by_creators(self, creators, all=False):
        """Searches based on creator/s."""
        if not self.db:
            raise NotInitalized()
        async with self.db.cursor() as cursor:
            param_string = ("creator_name = ? OR " * len(creators))[:-3]
            res = await (await cursor.execute(QUERIES["CREATOR_SEARCH"].format(param_string), creators)).fetchall()
            r = {}
            for row in res:
                if row['manga_id'] in r:
                    r[row['manga_id']].creators.append(row['creator_name'])
                else:
                    r[row['manga_id']] = manga.Manga(row)
            return list(r.values())

    async def get_chapters(self, manga_id):
        """Fetches all the chapters of manga_id"""
        if not self.db:
            raise NotInitalized()
        async with self.db.cursor() as cursor:
            res = await (await cursor.execute(QUERIES["CHAPTERS_FETCH"], (manga_id,))).fetchall()
            return [chapter.Chapter(i) for i in res]

    async def get_chapter(self, manga_id, number):
        """Fetches specific chapter number of manga_id"""
        if not self.db:
            raise NotInitalized()
        async with self.db.cursor() as cursor:
            res = await (await cursor.execute(QUERIES["CHAPTER_FETCH"], (manga_id, number,))).fetchone()
            if not res:
                raise ChapterNotFound(manga_id, number)
            return chapter.Chapter(res)