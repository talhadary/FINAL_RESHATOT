import asyncio

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
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: QUICClientProtocol(self),
            remote_addr=SERVER_ADDRESS
        )
        print("Connection established")

    async def send_file(self, filename):
        with open(filename, 'rb') as file:
            while True:
                chunk = file.read(BUFFER_SIZE)
                if not chunk:
                    break
                self.transport.sendto(chunk)
                await asyncio.sleep(0.01)  # Simulate some delay

        self.transport.sendto(b'EOF')
        print("File sent")


async def main():
    client = QUICClient()
    await client.connect()

    # Simulate file transfer
    await client.send_file('File.txt')

    print("Client closed")

if __name__ == "__main__":
    asyncio.run(main())
