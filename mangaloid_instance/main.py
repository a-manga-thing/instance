from aiohttp.web import Application as HTTP
from aiohttp.web import _run_app, get, json_response
from aiohttp import ClientSession
from asyncio import get_event_loop, Queue, gather
from logging import info, error, warn
from os import listdir, path, makedirs
from shutil import copy

from .version import VERSION
from .config import config
from .storage import database
from .storage.models import sync as sync_model
from .api import manga_routes, admin_routes
from . import sync

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
        try:
            makedirs(self.config.thumbnail_path, exist_ok=True)
        except:
            pass
        try:
            for i in listdir("../helpers"):
                copy(path.join("../helpers", i), self.config.thumbnail_path)
        except FileNotFoundError:
            print("../helpers not found\nYou're probably using a pip installation.\nIf you want to use the helper pages copy them manually to the thumbnail directory")
        except Exception as e:
            print("Could not install helpers: {}".format(e))

        manga_routes.Routes(self)
        admin_routes.Routes(self)
        sync.Routes(self.sync_manager)

        await self.db.init()
        return await gather(
            _run_app(self.web, host="0.0.0.0", port=config.http_port),
            self.sync_manager.start()
        )

    def start(self):
        return get_event_loop().run_until_complete(self._main())

app = Application()
def run():
    app.start()

if __name__ == '__main__':
    run()