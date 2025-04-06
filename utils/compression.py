import zlib


class CompressionHandler:
    """
    Class that handles compression and decompression of data using zlib.
    """
    def __init__(self):
        self.compression_enabled = False
        self.compression_threshold = -1  # -1 means that the compression is disabled

    def enable_compression(self, threshold: int) -> None:
        """
        Enable compression with the specified threshold.

        :param threshold: The threshold to enable compression.
        """
        self.compression_enabled = True
        self.compression_threshold = threshold

    @staticmethod
    def decompress(data: bytes) -> bytes:
        """
        Decompress data using zlib.

        :param data: The data to decompress.
        :return bytes: The decompressed data.
        """
        return zlib.decompress(data)

    @staticmethod
    def compress(data: bytes) -> bytes:
        """
        Compress data using zlib.

        :param data: The data to compress.
        :return bytes: The compressed data.
        """
        return zlib.compress(data)
