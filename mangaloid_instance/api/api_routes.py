from aiohttp.web import get, static, json_response, HTTPBadRequest, HTTPFound
from os import path
from config import config

class InvalidInput(HTTPBadRequest):
    def __init__(self):
        super().__init__(text="You either did not provide a necessary parameter or it is of the wrong type")

class TooManyTags(HTTPBadRequest):
    def __init__(self):
        super().__init__(text="You can only have max {} genres".format(config.max_tags))

class ApiRoutes:
    def __init__(self, instance):
        self.instance = instance
        self.instance.web.add_routes([
            get("/info", self.info),
            get("/manga/from_id", self.from_id),
            get("/manga/search", self.search),
            get("/manga/get_chapters", self.get_chapters),
            get("/manga/thumbnail", self.thumbnail),
            static("/thumbnail", config.thumbnail_path)
        ])

    async def info(self, request):
        return json_response(self.instance.to_dict())

    async def from_id(self, request):
        try:
            query_id = int(request.query.get("id"))
        except Exception as e:
            raise InvalidInput()
        manga = await self.instance.db.get_manga_by_id(query_id)
        return json_response(manga.to_dict())

    async def search(self, request):
        title = request.query.get("title")
        author = request.query.get("author")
        artist = request.query.get("artist")
        genres = request.query.get("genres")
        if genres:
            genres = [i.strip() for i in genres.split(",")]
            if len(genres) > config.max_tags:
                raise TooManyTags()
        manga = await self.instance.db.search(title=title, author=author, artist=artist, tags=genres)
        return json_response([i.to_dict() for i in manga])

    async def get_chapters(self, request):
        try:
            query_id = int(request.query.get("id"))
        except Exception as e:
            raise InvalidInput()
        chapters = await self.instance.db.get_chapters(query_id)
        return json_response([i.to_dict() for i in chapters])

    async def thumbnail(self, request):
        try:
            query_id = int(request.query.get("id"))
        except Exception as e:
            raise InvalidInput()
        raise HTTPFound("/thumbnail/{}".format())