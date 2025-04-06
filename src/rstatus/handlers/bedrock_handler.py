import struct
import time

from typing import Optional

from ..utils.client import MinecraftClient
from ..models.bedrock_server_data import BedrockServerResponse, MOTD, Version, Players


class BedrockHandler:
    def __init__(self, client: MinecraftClient):
        """
        Initialize a new BedrockHandler instance with a MinecraftClient.

        :param client: An instance of MinecraftClient used to communicate with the server.
        """
        self.client = client
        self.bot_response_protocol: int = 0
        self.extra_bool = False

    def _bedrock_server_status(self) -> Optional[BedrockServerResponse]:
        """
        Get the status of a Bedrock server by sending a ping request and parsing the response.

        :return Optional[BedrockServerResponse]: The parsed server response data or None if an error occurred.
        """
        try:
            start_time: float = time.time()  # The start time of the request

            # Start the connection
            self.client.connect(server_type='bedrock')

            # Send the ping packet
            PACKET_ID_UNCONNECTED_PING: bytes = b'\x01'
            timestamp: int = int(time.time() * 1000)
            time_bytes: bytes = struct.pack('>Q', timestamp)
            MAGIC: bytes = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
            client_guid: int = 0
            client_guid_bytes: bytes = struct.pack('>Q', client_guid)
            ping_packet: bytes = PACKET_ID_UNCONNECTED_PING + time_bytes + MAGIC + client_guid_bytes
            self.client.sock.sendto(ping_packet, (self.client.server_address, self.client.server_port))

            # Receive the response
            data, _ = self.client.sock.recvfrom(4096)

            if self.debug:
                print(f'Received data: {data}')

            # Calculate the response time in milliseconds
            response_time = (time.time() - start_time) * 1000

            # Parse the status response data
            server_data: Optional[BedrockServerResponse] = self._parse_bedrock_response(data)

            if server_data:
                server_data.ping = int(response_time)

            return server_data

        except Exception as e:
            if self.client.debug:
                print(f'Error getting server status: {e}')

            return None

        finally:
            self.client.close()

    def _parse_bedrock_response(self, data: bytes) -> Optional[BedrockServerResponse]:
        """
        Parse the response received from the Bedrock server.

        :param data: The raw byte data received from the server.
        :return Optional[BedrockServerResponse]: A structured response object or None if parsing fails.
        """
        offset: int = 0

        try:
            # Check if the packet is a unconnected pong packet
            if data[offset] != 0x1c:
                if self.debug:
                    print('Invalid packet type (Unconnected Pong)')
                return None

            offset += 1

            # Read the time sent (8 bytes)
            time_sent, = struct.unpack_from('>Q', data, offset)
            offset += 8

            # Read server GUID (8 bytes)
            server_guid, = struct.unpack_from('>Q', data, offset)
            offset += 8

            # Read the magic bytes (16 bytes)
            MAGIC: bytes = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
            magic: bytes = data[offset:offset + 16]

            if magic != MAGIC:
                if self.debug:
                    print('Invalid magic bytes. Expected: 0x00FFFFFF00FEFEFEFEFDFDFD12345678')
                return None

            offset += 16

            # Read the length of the server ID string (2 bytes)
            server_id_length, = struct.unpack_from('>H', data, offset)
            offset += 2

            # Read the server ID string
            server_id: str = data[offset:offset + server_id_length].decode('utf-8')
            offset += server_id_length

            if self.debug:
                print(f'Received server ID: {server_id}')

            # Split the server ID string
            response_data = server_id.split(';')

            # Check if the response data is valid
            if len(response_data) < 6:
                if self.debug:
                    print('Invalid response data')
                return None

            # Parse the response data
            motd: MOTD = MOTD(text=response_data[1], original=response_data[1])
            version: Version = Version(text=response_data[3], original=response_data[3], protocol=int(response_data[2]))
            players: Players = Players(online=int(response_data[4]), max=int(response_data[5]))
            server_data: BedrockServerResponse = BedrockServerResponse(
                ip_address=self.client.server_address,
                port=self.client.server_port,
                motd=motd,
                version=version,
                players=players,
                guid=server_guid,
                gamemode=response_data[8] if len(response_data) > 8 else '',
                brand=response_data[0],
                map=response_data[7] if len(response_data) > 7 else '',
                ping=0,
                raw_response=response_data
            )
            return server_data

        except Exception as e:
            if self.debug:
                print(f'Error parsing Bedrock server response: {e}')

            return None
