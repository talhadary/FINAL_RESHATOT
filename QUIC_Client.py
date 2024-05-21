import asyncio

# Constants
SERVER_ADDRESS = ('localhost', 1234)
BUFFER_SIZE = 1024


class QUICClientProtocol:
    def __init__(self, client):
        self.client = client

    def connection_made(self, transport):
        print("Connected to server")
        self.transport = transport

    def connection_lost(self, exc):
        self.client.connection_lost()
        print("Connection lost")

    def datagram_received(self, data, addr):
        # Process received data if needed
        pass


class QUICClient:
    def __init__(self):
        self.transport = None

    async def connect(self):
        self.transport, _ = await asyncio.get_event_loop().create_datagram_endpoint(
            lambda: QUICClientProtocol(self),
            remote_addr=SERVER_ADDRESS
        )
        print("Connection established")

    async def send_file(self, filename):
        # Read file and send it in packets
        with open(filename, 'rb') as file:
            while True:
                chunk = file.read(BUFFER_SIZE)
                if not chunk:
                    break
                self.transport.sendto(chunk)
                await asyncio.sleep(0.01)  # Simulate some delay

        # Send EOF marker
        self.transport.sendto(b'EOF')
        print("File sent")

    def connection_lost(self):
        # Perform cleanup tasks here
        pass


async def main():
    client = QUICClient()
    await client.connect()

    # Simulate file transfer
    await client.send_file('File.txt')

    client.connection_lost()
    print("Client closed")


if __name__ == "__main__":
    asyncio.run(main())
