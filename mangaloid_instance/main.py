from aiohttp.web import Application as HTTP
from aiohttp.web import _run_app, get, json_response
from aiohttp import ClientSession
from asyncio import get_event_loop, Queue, gather
from logging import info, error, warn
from json import load

from version import VERSION
from config import config
from storage import database
from storage.models import sync as sync_model
from api import manga_routes, admin_routes
import sync


async def import_from_json(self):
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


class Application(sync_model.Instance):
    def __init__(self):
        self.config = config
        self.context = {"subscribe_confirmations": []}
        self.client = ClientSession()
        
        self.web = HTTP()
        self.web.on_startup.append(self._startup_tasks)
        self.web.add_routes([get("/info", self._info)])

        self.db = database.Database(config.database)
        self.sync_manager = sync.SyncManager(self)

    async def _info(self, _):
        return json_response({
            "name": config.instance_name,
            "address": config.instance_address,
            "operator": config.instance_operator,
            "icon": config.instance_icon,
            "description": config.instance_description,
            "version": VERSION
        })

    async def _startup_tasks(self, app):
        pass

    async def _main(self):
        manga_routes.Routes(self)
        admin_routes.Routes(self)
        sync.Routes(self)

        await self.db.init()

        #await import_from_json(self)
        return await gather(
            _run_app(self.web, host="0.0.0.0", port=config.http_port),
            self.sync_manager.start()
        )

    def start(self):
        return get_event_loop().run_until_complete(self._main())


def run():
    Application().start()

if __name__ == '__main__':
    run()