import struct
import uuid
from typing import Optional, Tuple, Union, Dict

from ..utils.compression import CompressionHandler


class MinecraftPacket:
    """ Base class for Minecraft packets """
    def __init__(self):
        self.data: bytes = b''

    @staticmethod
    def encode_varint(value: int) -> bytes:
        """
        Encode an integer as a VarInt
        
        :param value: The integer to encode.
        :return bytes: The encoded VarInt.
        """
        result: bytes = b''

        while True:
            byte: int = value & 0x7F
            value >>= 7

            if value != 0:
                byte |= 0x80

            result += struct.pack('B', byte)

            if value == 0:
                break

        return result

    @staticmethod
    def pack_data(data: bytes) -> bytes:
        """ 
        Encodes the data with its length as a VarInt 
        
        :param data: The data to encode.
        :return bytes: The encoded data.
        """
        return MinecraftPacket.encode_varint(len(data)) + data

    @staticmethod
    def encode_string_varint(value: str) -> bytes:
        """ 
        Encode a string as a VarInt length-prefixed UTF-8 string 
        
        :param value: The string to encode.
        :return bytes: The encoded string.
        """
        encoded: bytes = value.encode('utf-8')
        return MinecraftPacket.encode_varint(len(encoded)) + encoded
    
    @staticmethod
    def encode_int(value: int) -> bytes:
        """ 
        Encode an integer as a 4-byte big-endian value 
        
        :param value: The integer to encode.
        :return bytes: The encoded integer.
        """
        return struct.pack('>i', value)
    
    @staticmethod
    def encode_long(value: int) -> bytes:
        return struct.pack('>q', value)

    @staticmethod
    def write_uuid(uuid_value: uuid.UUID) -> bytes:
        """
        Writes a UUID in the correct format (16 bytes, big-endian).
        
        :param uuid_value: The UUID to write.
        :return bytes: The UUID bytes.
        """
        return uuid_value.bytes

    def build_packet(self, packet_id: int, compression_handler: Optional[CompressionHandler] = None) -> bytes:
        """
        Build the complete packet with the packet ID and data, considering compression if enabled.
        
        :param packet_id: The packet ID.
        :param compression_handler: The compression handler to use.
        :return bytes: The full packet.
        """
        packet_data: bytes = self.encode_varint(packet_id) + self.data

        if compression_handler and compression_handler.compression_enabled:
            uncompressed_length = len(packet_data)
            if uncompressed_length >= compression_handler.compression_threshold:
                # Compress the data
                compressed_data = compression_handler.compress(packet_data)
                uncompressed_length_bytes = self.encode_varint(uncompressed_length)
                data = uncompressed_length_bytes + compressed_data
            else:
                # Do not compress, set uncompressed length to 0
                uncompressed_length_bytes = self.encode_varint(0)
                data = uncompressed_length_bytes + packet_data

            # Compute packet length (uncompressed length + data)
            packet_length_bytes = self.encode_varint(len(data))
            full_packet = packet_length_bytes + data
        else:
            # No compression, packet is as before
            full_packet = self.pack_data(packet_data)

        return full_packet

    @staticmethod
    def read_varint_from_data(data: bytes) -> Tuple[int, int]:
        """
        Reads a VarInt from the data provided.

        :param data: The data to read the VarInt from.
        :return Tuple[int, int]: The VarInt value and the total bytes read.
        """
        num_read: int = 0
        result: int = 0
        index: int = 0

        while True:
            if index >= len(data):
                raise Exception('Could not read VarInt from data')

            byte: int = data[index]
            index += 1
            result |= (byte & 0x7F) << (7 * num_read)
            num_read += 1

            if num_read > 5:
                raise Exception('VarInt is too big')

            if not (byte & 0x80):
                break

        return result, index

    @staticmethod
    def read_string_from_data(data: bytes) -> Tuple[str, int]:
        """
        Reads a string from the data provided.

        :param data: The data to read the string from.
        :return Tuple[str, int]: The string value and the total bytes read.
        """
        # Read the string length
        string_length, index = MinecraftPacket.read_varint_from_data(data)

        # Read the string data and decode it
        string_data = data[index:index + string_length]
        string = string_data.decode('utf-8')

        # Calculate the total bytes read
        total_bytes_read: int = index + string_length
        return string, total_bytes_read

    @staticmethod
    def parse_chat(chat_data: Union[Dict, str]) -> str:
        """
        Parse the chat data and return the text.

        :param chat_data: The chat data to parse.
        :return str: The parsed chat text.
        """
        if isinstance(chat_data, str):
            return chat_data

        elif isinstance(chat_data, dict):
            text: str = ''

            if 'text' in chat_data:
                text += chat_data['text']

            if 'extra' in chat_data and isinstance(chat_data['extra'], list):
                for item in chat_data['extra']:
                    text += MinecraftPacket.parse_chat(item)

            if 'translate' in chat_data:
                translate_key = chat_data['translate']
                with_list = chat_data.get('with', [])
                translated_text = f"{translate_key}: {' '.join(map(str, with_list))}"
                text += translated_text

            return text

        else:
            return str(chat_data)
