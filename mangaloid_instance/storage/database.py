from asyncio import get_event_loop
from aiohttp.web import HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm import declarative_base, sessionmaker, selectinload
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.sql import select
from sqlalchemy import or_, not_
from .models import Base, chapter, manga, creators
from datetime import datetime

class MangaNotFound(HTTPNotFound):
    def __init__(self, manga_id):
        super().__init__(text="Could not find manga with ID {}".format(manga_id))

class ChapterNotFound(HTTPNotFound):
    def __init__(self, manga_id, chapter):
        if chapter.is_integer():
            chapter = int(chapter)
        super().__init__(text="Could not find chapter {} of manga {}".format(chapter, manga_id))

class MandatoryParameter(HTTPBadRequest):
    def __init__(self, param):
        super().__init__(text="You have to provide {}".format(param))
        print(param)

def get_mandatory_parameter(dc, param, t=list):
    if not param in dc or type(dc[param]) is not t:
        raise MandatoryParameter(param)
    return dc[param]

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.engine = create_async_engine("sqlite+aiosqlite:///{}".format(self.db_path))
    
    async def init(self):
        base = Base
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            self.session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)()

    async def create_manga(self, *args, **kwargs):
        """
        Creates a new manga entry. ID is set by the database.
        Args (* means mandatory):
            type: Manga, Webtoon. Defaults to Manga
            *country_of_origin (str) : ISO-3166 Country Code
            *publication_status (str): Ongoing, Axed, Completed
            *scanlation_status (bool): Is completely scanlated
            mal_id (int): MyAnimeList ID
            anilist_id (int): AniList ID
            mu_id (int): MangaUpdates ID
        
        Returns Manga object as present in the database.
        """
        statement = manga.Manga(
            content_type=manga.Types[get_mandatory_parameter(kwargs, "type", str)],
            country_of_origin=get_mandatory_parameter(kwargs, "country_of_origin", str).strip()[0:2],
            publication_status=manga.PubStatuses[get_mandatory_parameter(kwargs, "publication_status", str)],
            scanlation_status=get_mandatory_parameter(kwargs, "scanlation_status", bool),
            mal_id=int(kwargs.get("mal_id", 0)),
            anilist_id=int(kwargs.get("anilist_id", 0)),
            mu_id=int(kwargs.get("mangaupdates_id", 0))
        )
        statement.authors.extend([creators.Person(name=i) for i in get_mandatory_parameter(kwargs, "authors")])
        statement.artists.extend([creators.Person(name=i) for i in get_mandatory_parameter(kwargs, "artists")])
        statement.titles.extend([manga.Title(title=i) for i in get_mandatory_parameter(kwargs, "titles")])
        statement.genres.extend([manga.Genre(name=i) for i in get_mandatory_parameter(kwargs, "genres")])
        self.session.add(statement)
        await self.session.commit()
        return statement

    async def create_chapter(self, manga_id, **kwargs):
        """
        Creates a new chapter entry. ID is set by the database.
        Args (* means mandatory):
            *chapter_no (int)
            chapter_postfix (str)
            *page_count (int)
            *title (str)
            version (int)
            *language (str) : ISO 639-1 Language code
            date_added (datetime): Defaults to current datetime
            *ipfs_link (str): IPFS CID to chapter directory
        Returns Chapter object as present in the database.
        """
        statement = chapter.Chapter(
            manga_id=manga_id,
            chapter_no=get_mandatory_parameter(kwargs, "chapter_no", int),
            chapter_postfix=kwargs.get("chapter_postfix", ""),
            page_count=get_mandatory_parameter(kwargs, "page_count", int),
            title=get_mandatory_parameter(kwargs, "title", str),
            version=kwargs.get("version", -1),
            language_id=get_mandatory_parameter(kwargs, "language", str)[0:2],
            date_added=kwargs.get("date_added", datetime.now()),
            ipfs_link=get_mandatory_parameter(kwargs, "ipfs_link", str)
        )
        self.session.add(statement)
        await self.session.commit()
        return statement

    async def get_manga_by_id(self, manga_id):
        """
        Fetches manga by id
        Args:
            *manga_id (positional) (int)
        
        Returns Manga object.
        """
        statement = select(manga.Manga).where(manga.Manga.id == manga_id).options(*manga.Manga._query_options)
        result = (await self.session.execute(statement)).scalars().first()
        if not result:
            raise MangaNotFound(manga_id)
        return result

    async def search(self, title=None, author=None, artist=None, tags=None):
        """
        Searches manga database based on title, author, artist and genres/tags
        All of these are optional, can be used in any combination and are evaluated
        in that specific order.
        Args:
            title (str): This is tested in a case-insensitive LIKE clause.
            author (str): This is tested as "equals" and is case-sensitive.
            artist (str): This is tested as "equals" and is case-sensitive.
            tags (list): List of genres/tags. Can be prefixed with either + or -
                         to define inclusion/exclusion (if missing it defaults to +).
                         As for the tags themselves they are tested as "equal" 
                         and are case-sensitive.

        Returns list of Manga objects that match, or empty list if none found.
        """
        if not title and not author and not artist and not tags:
            return []
        statement = select(manga.Manga).options(*manga.Manga._query_options)
        if title:
            title_select = select(manga.Title).where(manga.Title.title.like("%{}%".format(title)))
            content = (await self.session.execute(title_select)).scalars().all()
            if not content:
                return []
            statement = statement.filter(or_(*[(manga.Manga.id == i.manga_id) for i in content]))
        if author:
            statement = statement.filter(manga.Manga.authors.any(name=author))
        if artist:
            statement = statement.filter(manga.Manga.artists.any(name=artist))
        if tags:
            for tag in tags:
                if tag.startswith("-"):
                    statement = statement.filter(not_(manga.Manga.genres.any(name=tag[1:])))
                else:
                    if tag.startswith("+"):
                        tag = tag[1:]
                    statement = statement.filter(manga.Manga.genres.any(name=tag))
        result = (await self.session.execute(statement)).scalars().all()
        return result or []

    async def get_chapters(self, manga_id):
        """
        Fetches chapters of manga with provided ID
        Args:
            *manga_id (positional) (int)
        
        Returns list of Chapter objects or empty list if manga is not found or has no chapters.
        """
        statement = select(chapter.Chapter).where(chapter.Chapter.manga_id == manga_id)
        result = (await self.session.execute(statement)).scalars().all()
        return result or []