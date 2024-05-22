import asyncio
from rx import create
from rx.operators import observe_on
from rx.scheduler.eventloop import AsyncIOScheduler
from rx.disposable import Disposable

# Constants
SERVER_ADDRESS = ('localhost', 1234)
BUFFER_SIZE = 1024


class QUICClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, client):
        self.transport = None
        self.client = client

    def connection_made(self, transport):
        print("Connected to server")
        self.transport = transport
        self.client.transport = transport

    def connection_lost(self, exc):
        print("Connection lost")

    def datagram_received(self, data, addr):
        if data == b'EOF':
            print("File transfer completed")
            self.transport.close()


class QUICClient:
    def __init__(self):
        self.transport = None

    async def connect(self):
        loop = asyncio.get_running_loop()
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: QUICClientProtocol(self),
            remote_addr=SERVER_ADDRESS
        )
        print("Connection established")

    def send_file(self, filename):
        def on_subscribe(observer, scheduler):
            async def read_and_send():
                with open(filename, 'rb') as file:
                    while True:
                        chunk = file.read(BUFFER_SIZE)
                        if not chunk:
                            break
                        self.transport.sendto(chunk)
                        observer.on_next(chunk)
                        await asyncio.sleep(0.01)  # Simulate some delay
                self.transport.sendto(b'EOF')
                observer.on_completed()

            asyncio.ensure_future(read_and_send())

            return Disposable(lambda: print("Disposed"))

        return create(on_subscribe).pipe(
            observe_on(AsyncIOScheduler(asyncio.get_event_loop()))
        )


async def main():
    client = QUICClient()
    await client.connect()
    file_observable = client.send_file('File.txt')
    file_observable.subscribe(
        on_next=lambda chunk: print(f"Sent chunk: {len(chunk)} bytes"),
        on_completed=lambda: print("File sent"),
        on_error=lambda e: print(f"Error: {e}")
    )

if __name__ == "__main__":
    asyncio.run(main())
