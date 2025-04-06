import socket
from typing import Union, Optional

import socks

from .compression import CompressionHandler
from ..packets.base import MinecraftPacket


class MinecraftClient:
    def __init__(
            self,
            server_address: str,
            server_port: int = 25565,
            timeout: int = 5,
            bungeehack: bool = False,
            proxy_type: Optional[str] = None,
            proxy_address: Optional[str] = None,
            proxy_port: Optional[int] = None,
            debug: bool = False,
    ):
        """
        Initialize a new MinecraftClient instance with server and connection settings.

        :param server_address: The address of the Minecraft server.
        :param server_port: The port number of the server (default is 25565).
        :param timeout: Timeout in seconds for socket operations.
        :param bungeehack: Flag to enable BungeeCord hack.
        :param proxy_type: Type of proxy to use ("socks4" or "socks5"), if any.
        :param proxy_address: The address of the proxy server.
        :param proxy_port: The port of the proxy server.
        :param debug: Flag to enable debug logging.
        """
        self.server_address: str = server_address
        self.server_port: int = server_port
        self.timeout: int = timeout
        self.bungeehack: bool = bungeehack
        self.sock: Union[socket.socket, None] = None
        self.compression_handler = CompressionHandler()

        # Proxy settings
        self.proxy_type: Optional[str] = proxy_type
        self.proxy_address: Optional[str] = proxy_address
        self.proxy_port: Optional[int] = proxy_port
        self.debug: bool = debug

    def connect(self, server_type: str = 'java') -> None:
        """
        Establish a TCP connection to the Minecraft server, optionally through a proxy.

        :param server_type: Type of the server ("java" or other), affects socket type.
        :return None: This function does not return a value.
        """
        # Check if the proxy settings are valid
        if self.proxy_type and self.proxy_address and self.proxy_port:
            # Check if the proxy type is valid
            if self.proxy_type.lower() == 'socks4':
                proxy_type = socks.SOCKS4

            elif self.proxy_type.lower() == 'socks5':
                proxy_type = socks.SOCKS5

            else:
                raise ValueError('Proxy type must be either "socks4" or "socks5"')

            # Create a socket with the proxy settings
            self.sock = socks.socksocket()
            self.sock.settimeout(self.timeout)
            self.sock.set_proxy(
                proxy_type=proxy_type,
                addr=self.proxy_address,
                port=self.proxy_port
            )

            if self.debug:
                print(
                    f'Connecting to {self.server_address}:{self.server_port} through proxy {self.proxy_address}:{self.proxy_port} ({self.proxy_type.upper()})')

        else:
            # Connect to the server without a proxy
            if server_type == 'java':
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(self.timeout)

            else:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.settimeout(self.timeout)

            if self.debug:
                print(f'Connecting to {self.server_address}:{self.server_port} (without proxy)')

        if server_type == 'java':
            self.sock.connect((self.server_address, self.server_port))

    def close(self) -> None:
        """
        Close the existing TCP connection to the server.

        :return None: This function does not return a value.
        """
        if self.sock:
            self.sock.close()
            self.sock = None

    def _receive_packet(self) -> bytes:
        """
        Receive a packet from the socket and return the packet data.
        Handles reading the packet length, receiving data in chunks, and decompressing if needed.

        :return bytes: The packet data received from the socket.
        """
        packet_length: int = self._read_varint()
        packet_data: bytes = b''

        # Read the packet data
        while len(packet_data) < packet_length:
            # Read a chunk of data from the socket
            chunk: bytes = self.sock.recv(packet_length - len(packet_data))

            # Check if the connection was lost while reading the packet data
            if not chunk:
                raise Exception(
                    f'Connection lost while reading packet data (expected {packet_length} bytes, got {len(packet_data)} bytes)')

            packet_data += chunk  # Append the chunk to the packet data

        # Check if the compression is enabled and decompress the packet data if needed
        if self.compression_handler.compression_enabled:
            # Read the uncompressed length of the packet
            uncompressed_length, index = MinecraftPacket.read_varint_from_data(packet_data)

            if uncompressed_length > 0:  # Check if the packet is compressed
                compressed_data = packet_data[index:]
                packet_data = self.compression_handler.decompress(compressed_data)

            else:
                packet_data = packet_data[index:]

        return packet_data

    def _read_varint(self) -> int:
        """
        Read a VarInt from the socket and return the value.
        A VarInt is a variable-length integer used in the Minecraft protocol.

        :return int: The VarInt value read from the socket.
        """
        num_read: int = 0
        result: int = 0

        while True:
            byte: bytes = self.sock.recv(1)

            if not byte:
                raise Exception('Connection lost while reading VarInt')

            byte_value: int = byte[0]
            result |= (byte_value & 0x7F) << (7 * num_read)
            num_read += 1

            if num_read > 5:
                raise Exception(f'VarInt is too big (more than 5 bytes): {result}')

            if not (byte_value & 0x80):
                break

        return result
