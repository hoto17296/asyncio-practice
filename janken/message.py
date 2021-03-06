import re
import json
import asyncio
from pyee import EventEmitter


class MessageConnection(EventEmitter):

    def __init__(self, reader=None, writer=None):
        super().__init__()
        self.reader = reader
        self.writer = writer
        if writer:
            self.address = writer.get_extra_info('peername')

    async def connect(self, host, port):
        self.reader, self.writer = await asyncio.open_connection(host, port)
        self.address = self.writer.get_extra_info('peername')
        self.emit('connect')
        await self.listen()

    def send(self, event, *args, **kwargs):
        assert(self.writer)
        assert(type(event) is str and re.compile(r'^\w+$').match(event))
        message = '%s\t%s\n' % (event, json.dumps([args, kwargs]))
        self.writer.write(message.encode())

    async def listen(self):
        assert(self.reader)
        pattern = re.compile(r'^(\w+?)\t(.*)\n$')
        while True:
            message = await self.reader.readline()
            if message:
                matched = pattern.match(message.decode())
                assert(matched)
                event, data = matched.groups()
                args, kwargs = json.loads(data)
                self.emit(event, *args, **kwargs)
            else:
                self.emit('disconnect')
                return

    def close(self):
        self.writer.close()


class MessageServer(EventEmitter):

    async def start(self, **kwargs):
        self.server = await asyncio.start_server(self.handler, **kwargs)

    async def handler(self, reader, writer):
        connection = MessageConnection(reader, writer)
        self.emit('connect', connection)
        await connection.listen()

    async def close(self):
        self.server.close()
        await self.server.wait_closed()
