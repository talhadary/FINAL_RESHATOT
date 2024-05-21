import asyncio
import random

# Constants
SERVER_ADDRESS = ('localhost', 1234)
BUFFER_SIZE = 1024


class QUICServerProtocol:
    def __init__(self, server):
        self.server = server

    def connection_made(self, transport):
        print("Client connected")
        self.transport = transport

    def connection_lost(self, exc):
        self.server.connection_lost()
        print("Client disconnected")

    def datagram_received(self, data, addr):
        # Simulate packet loss
        if random.random() < 0.1:  # Simulating 10% packet loss
            return

        # Handle incoming datagram
        self.server.packets_received += 1
        self.server.total_packet_rate += len(data)

        # Process the data (simulate file transfer)
        # For simplicity, assume each packet contains a part of the file
        if data.endswith(b'EOF'):
            self.server.files_received += 1
            print("File received")
        else:
            self.server.total_data_rate += len(data)


class QUICServer:
    def __init__(self):
        self.transport = None
        self.files_received = 0
        self.packets_received = 0
        self.total_data_rate = 0
        self.total_packet_rate = 0

    async def serve(self):
        self.transport, _ = await asyncio.get_event_loop().create_datagram_endpoint(
            lambda: QUICServerProtocol(self),
            local_addr=SERVER_ADDRESS
        )
        print("Server started")

        # Keep the server running indefinitely
        while True:
            await asyncio.sleep(1)  # Adjust as needed

    def connection_lost(self):
        # Perform cleanup tasks here
        pass


async def main():
    server = QUICServer()
    await server.serve()
    print("Server closed")


if __name__ == "__main__":
    asyncio.run(main())
