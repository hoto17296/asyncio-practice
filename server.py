import logging
from message import MessageServer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('janken.server')


class Env:

    def __init__(self):
        self.clients = []

    def on_connect(self, connection):
        client = Client(connection)
        self.clients.append(client)
        logger.info('connected')


class Client:

    def __init__(self, connection):
        self.connection = connection
        connection.on('disconnect', self.on_disconnect)

    def on_disconnect(self):
        logger.info('disconnected')


if __name__ == '__main__':
    server = MessageServer()
    server.on('connect', Env().on_connect)
    server.start(port=8888)
