from asyncio import Queue
from .utils import create_sync_payload
from enum import Enum
from aiohttp import ClientSession
from logging import getLogger

class SyncEvents(Enum):
    CREATE = 1
    MODIFY = 2
    DELETE = 3

class SyncItem:
    def __init__(self, payload, event):
        self.payload = payload.to_dict()
        self.event_type = event
        self.item_type = payload.__name__

    async def get_body(self, instance, self_address):
        payload = await create_sync_payload(self.payload, instance.public_key)
        return {
            "action" : self.event_type.name,
            "item_type" : self.item_types,
            "instance" : self_address,
            "payload" : payload
        }

class SyncManager:
    def __init__(self, ctx):
        self.db = ctx.db
        self.address = ctx.config.instance_address
        self.queue = Queue()
        self.http = ClientSession()
        self.logger = getLogger("sync-manager")

    def add(self, obj):
        self.queue.put_nowait(SyncItem(obj, SyncEvents.CREATE))

    def update(self, obj):
        self.queue.put_nowait(SyncItem(obj, SyncEvents.MODIFY))

    def remove(self, obj):
        self.queue.put_nowait(SyncItem(obj, SyncEvents.DELETE))

    async def start(self):
        self.logger.info("Starting sync manager loop")
        while True:
            item = await self.queue.get()
            instances = await self.db.select_all_instances()
            for instance in instances:
                try:
                    body = item.get_body(instance, self.address)
                    r = await self.http.post(instance.address, json=body)
                    if r.status == 403:
                        pass #TODO: Remove this instance
                except Exception as e:
                    self.logger.warn("Failed to send sync to {} ({})".format(instance.address, e))