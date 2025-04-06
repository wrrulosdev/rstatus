import struct
import uuid
from typing import Optional

from .base import MinecraftPacket


class LoginStartPacket(MinecraftPacket):
    """Login Start packet sent during the login process."""

    def __init__(self, username: str, login_packet_mode: int, debug: bool):
        super().__init__()
        if debug:
            print(f'[?] Login packet mode: {login_packet_mode}')

        if login_packet_mode == 0:
            self.data += self.encode_string_varint(username)
            
        if login_packet_mode == 1:
            self.data += b'\x00'
            
        if login_packet_mode == 2:
            self.data += self.encode_string_varint(username)
            self.data += b'\x00'
            self.data += b'\x00'

        if login_packet_mode == 3:
            self.data += self.encode_string_varint(username)
            player_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, username)
            self.data += MinecraftPacket.write_uuid(player_uuid)

        if login_packet_mode == 4:
            self.data += self.encode_string_varint(username)
            player_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, username)
            self.data += MinecraftPacket.write_uuid(player_uuid)
            self.data += b'\x00'
