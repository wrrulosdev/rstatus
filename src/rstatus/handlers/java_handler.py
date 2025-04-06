import struct
import time
import json
import uuid
from typing import Optional, Union

from ..packets import MinecraftPacket, HandshakePacket, LoginStartPacket
from ..utils.client import MinecraftClient
from ..models.java_server_data import JavaServerResponse, MOTD, Version, Players, ModInfo
from ..protocol.version import ProtocolVersion
from ..utils.clear import ClearResponse
from ..utils.response import BotResponse


class JavaHandler:
    def __init__(self, client: MinecraftClient):
        self.client = client
        self.bot_connection_attempts: int = 0
        self.last_bot_response: str = ''
        self.bot_response_protocol: int = 0
        self.login_packet_mode: int = 0
        self.extra_bool = False
        self.uuid = False

    def _java_server_status(self, bot: bool = True) -> Optional[JavaServerResponse]:
        """
        Get the status of the server and return the result.

        :return Optional[Dict]: The server status data or None if an error occurred.
        """
        try:
            start_time: float = time.time()  # The start time of the request

            # Start the connection
            self.client.connect()

            # Send the handshake packet with next state 1 (status)
            self._send_handshake(next_state=1)

            # Send the status request packet
            self._send_status_request()

            # Receive the response packet
            response_data: bytes = self._receive_packet()

            # Calculate the response time in milliseconds
            response_time = (time.time() - start_time) * 1000

            # Parse the status response data
            server_data: JavaServerResponse = self._parse_status_response(response_data, bot)

            # Add the ping time to the server data and return it
            server_data.ping = int(response_time)
            return server_data

        except Exception as e:
            if self.client.debug:
                print(f'Error getting server status: {e}')

            return None

        finally:
            self.client.close()

    def _bot_response(self, version: Union[str, int, None] = None) -> str:
        """
        Connect the bot to the server and return the result of the connection.

        :param version: The version of the server protocol to use (Version name or protocol number).
        :return str: The result of the bot connection.
        """
        if self.bot_connection_attempts >= 10:
            return f'Connection failed (Max attempts reached) - {self.last_bot_response}'

        username: str = 'Tarima'

        if version is None:
            server_status: Optional[JavaServerResponse] = self._java_server_status()

            if server_status is None:
                return 'Could not get server status.'

            protocol_version = server_status.version.protocol

        else:
            if str(version) == '120':
                return 'Connection failed (TCPShield Detected)'

            if str(version) == '-1':
                version = 47

            if isinstance(version, str):
                protocol_version = ProtocolVersion.get_protocol_by_version(version)

            else:
                protocol_version = version

        if ProtocolVersion.get_version_by_protocol(protocol_version) is None:
            if self.client.debug:
                print(f'Invalid protocol version: {protocol_version}. Using default version 47')

            protocol_version = 47

        self.bot_response_protocol = protocol_version

        if self.login_packet_mode == 5:
            self.login_packet_mode = -1
            protocol_version = 47
            time.sleep(5.5)

        if self.client.debug:
            print(f'Connecting bot with protocol version: {protocol_version}')

        try:
            # Start the connection
            self.client.connect()

            # Send the handshake packet with next state 2 (login)
            self._send_handshake(protocol_version, next_state=2)

            # Send the login start packet with the bot username
            self._send_login_start(username=username, protocol_version=protocol_version)

            # Handle the login response
            result: str = self._handle_login_response()
            self.last_bot_response = result

            if self.client.debug:
                print(f'Bot connection result: {result}')

            if 'ip forwarding' in result.lower():
                if self.client.debug:
                    print('Detected Network Port (IP Forwarding). Retrying connection with BungeeHack.')

                self.client.bungeehack = True
                self.bot_connection_attempts += 1
                result: str = self._bot_response(version=protocol_version)

            if 'io.netty.handler.codec' in result.lower():
                self.login_packet_mode += 1
                self.bot_connection_attempts += 1
                result: str = self._bot_response(version=protocol_version)

            if 'connection throttled! please wait before reconnecting' in result.lower():
                if self.client.debug:
                    print('Connection throttled. Retrying connection in 5.5 seconds.')

                time.sleep(5.5)
                self.bot_connection_attempts += 1
                result: str = self._bot_response(version=protocol_version)

            return result

        except Exception as e:
            if self.client.debug:
                print(f'Error connecting bot: {e}')

            return 'Connection failed'

        finally:
            self.client.close()

    def _send_handshake(self, protocol_version: int = 47, next_state: int = 1) -> None:
        """
        Sends a handshake packet to the server.

        :param protocol_version: The protocol version to use.
        :param next_state: The next state to switch to after the handshake (1=status, 2=login).
        """
        # Add the BungeeC ord IP forwarding data if enabled
        if self.client.bungeehack:
            player_uuid: uuid.UUID = uuid.uuid3(uuid.NAMESPACE_DNS, 'MCPTool')
            server_address: str = f'{self.client.server_address}\x00127.0.0.1\x00{player_uuid}'

        else:
            server_address = self.client.server_address

        # Create the handshake packet
        handshake: HandshakePacket = HandshakePacket(
            protocol_version=protocol_version,
            server_address=server_address,
            server_port=self.client.server_port,
            next_state=next_state
        )
        # Send the handshake packet
        self.client.sock.sendall(handshake.build_packet(0x00, compression_handler=self.client.compression_handler))

    def _send_status_request(self) -> None:
        """ Sends a status request packet to the server """
        self.client.sock.sendall(MinecraftPacket().build_packet(0x00))

    def _send_login_start(self, username: str, protocol_version: int) -> None:
        """
        Sends a login start packet to the server.

        :param username: The username of the bot to connect.
        """
        login_start: LoginStartPacket = LoginStartPacket(username=username, login_packet_mode=self.login_packet_mode, debug=self.client.debug)
        self.client.sock.sendall(login_start.build_packet(0x00, compression_handler=self.client.compression_handler))

    def _parse_status_response(self, data: bytes, bot: bool) -> JavaServerResponse:
        """
        Parse the status response data and return the server data.

        :param data: The status response data to parse.
        :return Dict: The server data parsed from the response.
        """
        # Parse the status response data
        packet_id, index = MinecraftPacket.read_varint_from_data(data)

        # Check if the packet ID is not 0x00
        if packet_id != 0x00:
            # The packet ID is not 0x00 (Status Response)
            raise Exception(f'Unexpected packet ID: {packet_id}')

        response_json, _ = MinecraftPacket.read_string_from_data(data[index:])
        original_server_data: dict = json.loads(response_json)

        if self.client.debug:
            print(f'Status Response: {original_server_data}')

        # Parse the MOTD
        motd_text: str = MinecraftPacket.parse_chat(original_server_data.get('description', ''))
        motd: MOTD = MOTD(text=ClearResponse.clear_response(motd_text), original=motd_text)

        # Parse the version
        version_response: str = MinecraftPacket.parse_chat(original_server_data.get('version', {}).get('name', ''))
        version_protocol: int = original_server_data.get('version', {}).get('protocol', 0)
        version: Version = Version(text=ClearResponse.clear_response(version_response), original=version_response, protocol=version_protocol,
                                   version_name=ProtocolVersion.get_version_by_protocol(version_protocol))

        # Parse the players
        players_online: int = original_server_data.get('players', {}).get('online', 0)
        players_max: int = original_server_data.get('players', {}).get('max', 0)
        players_sample: list = original_server_data.get('players', {}).get('sample', [])
        players: Optional[str] = None

        if players_sample != []:
            if self.client.debug:
                print(f'(1) Players sample: {players_sample}')
            player_list = [{'name': player['name'], 'id': player['id']} for player in players_sample]

            if self.client.debug:
                print(f'(2) Player list: {player_list}')

            if len(player_list) >= 1:
                players = ', '.join([player['name'] for player in player_list])

                if self.client.debug:
                    print(f'(3) Players: {players}')

        players_obj: Players = Players(online=players_online, max=players_max, players=players, sample=players_sample)

        # Parse the mod info
        mod_info_type: str = original_server_data.get('modinfo', {}).get('type', '')
        mod_info_list: list = original_server_data.get('modinfo', {}).get('modList', [])
        mod_info: ModInfo = ModInfo(type=mod_info_type, mod_list=mod_info_list)

        # Get the bot response
        bot_response: str = ClearResponse.clear_response(self._bot_response(version=version.protocol)) if bot else ''
        new_bot_response: str = BotResponse.custom_response(bot_response)

        # Create the JavaServerResponse object
        server_data: JavaServerResponse = JavaServerResponse(
            ip_address=self.client.server_address,
            port=self.client.server_port,
            motd=motd,
            version=version,
            players=players_obj,
            mod_info=mod_info,
            favicon=original_server_data.get('favicon', ''),
            ping=0,
            bot_response=new_bot_response,
            brand="",
            plugin_channels="",
            raw_response=original_server_data
        )
        return server_data

    def _handle_set_compression(self, data: bytes) -> None:
        """
        Handles the set compression packet.

        :param data: The data of the set compression packet.
        """
        threshold, _ = MinecraftPacket.read_varint_from_data(data)
        self.client.compression_handler.enable_compression(threshold)

        if self.client.debug:
            print(f'Compression enabled with threshold: {threshold}')

    def _handle_login_plugin_request(self, data: bytes) -> None:
        """
        Handles the login plugin request packet.

        :param data: The data of the login plugin request packet.
        """
        # Read the plugin message ID and channel name
        plugin_message_id, index = MinecraftPacket.read_varint_from_data(data)
        channel_name, _ = MinecraftPacket.read_string_from_data(data[index:])

        if self.client.debug:
            print(f'Plugin Message ID: {plugin_message_id}, Channel Name: {channel_name}')

        # Respond with Login Plugin Response (packet ID 0x02 in serverbound)
        response: MinecraftPacket = MinecraftPacket()
        response.data += response.encode_varint(plugin_message_id)
        response.data += struct.pack('>?', False)
        self.client.sock.sendall(response.build_packet(0x02, compression_handler=self.client.compression_handler))

    def _handle_login_response(self) -> str:
        """
        Handles the login response from the server.

        :return str: The result of the login response.
        """
        while True:
            packet: bytes = self._receive_packet()
            packet_id, index = MinecraftPacket.read_varint_from_data(packet)

            if self.client.debug:
                print(f'Received packet with ID: {packet_id}')

            if packet_id == 0x00:  # Disconnect
                reason_json, _ = MinecraftPacket.read_string_from_data(packet[index:])

                if self.client.debug:
                    print(f'Disconnect message: {reason_json}')

                try:
                    reason: dict = json.loads(reason_json)
                    message: str = MinecraftPacket.parse_chat(chat_data=reason)

                except json.JSONDecodeError:
                    message: str = reason_json

                return message

            elif packet_id == 0x01:  # Encryption Request
                return 'The server is in online mode'

            elif packet_id == 0x02:  # Login Success
                if self.client.bungeehack:
                    return 'Connected with BungeeHack'

                else:
                    return 'Connected'

            elif packet_id == 0x03:  # Set Compression
                self._handle_set_compression(packet[index:])

            elif packet_id == 0x04:  # Login Plugin Request
                self._handle_login_plugin_request(packet[index:])

            else:
                if self.client.debug:
                    print(f'Unknown packet ID: {packet_id}')

                return f'Connection failed - Unknown packet ID'

    def _receive_packet(self) -> bytes:
        """
        Receives a packet from the socket

        :return bytes: The packet data received from the socket.
        """
        packet_length: int = self._read_varint()
        packet_data: bytes = b''

        # Read the packet data
        while len(packet_data) < packet_length:
            # Receive the remaining data
            chunk: bytes = self.client.sock.recv(packet_length - len(packet_data))

            # Check if the connection was lost
            if not chunk:
                if self.client.debug:
                    print(f'Connection lost while reading packet data in bot response (expected {packet_length} bytes, got {len(packet_data)} bytes)')

                raise Exception('Connection lost while reading packet data')

            packet_data += chunk  # Add the chunk to the packet data

        # Check if compression is enabled and decompress the data if needed
        if self.client.compression_handler.compression_enabled:
            # Read the uncompressed length of the packet
            uncompressed_length, index = MinecraftPacket.read_varint_from_data(packet_data)

            if uncompressed_length > 0:  # Check if the packet is compressed
                compressed_data = packet_data[index:]
                packet_data = self.client.compression_handler.decompress(compressed_data)

            else:
                packet_data = packet_data[index:]

        return packet_data

    def _read_varint(self) -> int:
        """
        Reads a VarInt from the socket.

        :return int: The VarInt value read from the socket.
        """
        num_read: int = 0
        result: int = 0

        while True:
            byte: Union[bytes, int, None] = self.client.sock.recv(1)

            if not byte:
                raise Exception('Connection lost while reading VarInt')

            byte = ord(byte)

            result |= (byte & 0x7F) << (7 * num_read)
            num_read += 1

            if num_read > 5:
                raise Exception('VarInt is too big')

            if not (byte & 0x80):
                break

        return result
