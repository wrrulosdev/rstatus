import struct

from .base import MinecraftPacket


class HandshakePacket(MinecraftPacket):
    """ Handshake packet used to initiate a connection with the server """
    def __init__(self, protocol_version: int, server_address: str, server_port: int, next_state: int):
        super().__init__()
        self.data += self.encode_varint(protocol_version)
        self.data += self.encode_string_varint(server_address)
        self.data += struct.pack('>H', server_port)
        self.data += self.encode_varint(next_state)
