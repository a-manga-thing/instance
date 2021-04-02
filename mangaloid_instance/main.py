from aiohttp.web import Application as HTTP
from aiohttp.web import _run_app
from asyncio import get_event_loop

from config import config
from storage import database
from storage.models import instance
from api import api_routes

from json import load

class Application(instance.Instance):
    def __init__(self):
        self.web = HTTP()
        self.web.on_startup.append(self._background)
        self.db = database.Database(config.database)
        super().__init__(
            config.instance_name,
            config.instance_operator,
            config.instance_icon,
            config.instance_description
        )

    async def _background(self, app):
        """
        for i in load(open("db.json", "r")):
            manga = await self.db.create_manga(
                type="Manga",
                publication_status="Ongoing",
                country_of_origin="JP",
                scanlation_status=True,
                titles=i["titles"],
                artists=[i["artist"]],
                authors=[i["author"]],
                genres=i["genres"]
            )
            for c in i["chapters"]:
                await self.db.create_chapter(
                    manga.id,
                    chapter_no=c["no"],
                    page_count=c["pages"],
                    title=c["title"],
                    language="EN",
                    ipfs_link=c["cid"]
                )
        """
        
    async def _main(self):
        api_routes.ApiRoutes(self)
        await self.db.init()
        return await _run_app(self.web, host="0.0.0.0", port=config.http_port)

    def start(self):
        return get_event_loop().run_until_complete(self._main())

if __name__ == '__main__':
    Application().start()