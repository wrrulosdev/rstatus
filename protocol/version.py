from typing import Optional


class ProtocolVersion:
    _versions: dict[str, int] = {}

    def __init__(self, version: str, protocol: int):
        self.version = version
        self.protocol = protocol

    @classmethod
    def register(cls, version: str, protocol: int, subversions: Optional[list] = None) -> None:
        """
        Register a new protocol version.

        :param str version: Version name.
        :param int protocol: Protocol number.
        :param Optional[list] subversions: Subversions of the version.
        """
        cls._versions[version] = ProtocolVersion(version, protocol)

        if subversions:
            for subversion in subversions:
                cls._versions[subversion] = ProtocolVersion(subversion, protocol)

    @classmethod
    def get_version_by_protocol(cls, protocol: int) -> str:
        """
        Get the version name by its protocol number.

        :param int protocol: Protocol number.
        :return str: The version name.
        """
        for version, version_protocol in cls._versions.items():
            if version_protocol.protocol == protocol:
                return version

    @classmethod
    def get_protocol_by_version(cls, version: str) -> int:
        """
        Get the protocol number by its version name.

        :param str version: Version name.
        :return int: The protocol number.
        """
        return cls._versions.get(version, cls._versions.get('1.8')).protocol
    
    @classmethod
    def get_all_versions(cls) -> list[str]:
        """
        Get all registered versions.

        :return list[str]: A list of all registered versions.
        """
        return list(cls._versions.keys())
    
    @classmethod
    def initialize_versions(cls) -> None:
        """ Initialize all versions. """
        cls.register('1.8', 47, ['1.8.1', '1.8.2', '1.8.3', '1.8.4', '1.8.5', '1.8.6', '1.8.7', '1.8.8', '1.8.9'])
        cls.register('1.9', 107)
        cls.register('1.9.1', 108)
        cls.register('1.9.2', 109)
        cls.register('1.9.3', 110, ['1.9.4'])
        cls.register('1.10', 210, ['1.10.1', '1.10.2'])
        cls.register('1.11', 315)
        cls.register('1.11.1', 316, ['1.11.2'])
        cls.register('1.12', 335)
        cls.register('1.12.1', 338)
        cls.register('1.12.2', 340)
        cls.register('1.13', 393)
        cls.register('1.13.1', 401)
        cls.register('1.13.2', 404)
        cls.register('1.14', 477)
        cls.register('1.14.1', 480)
        cls.register('1.14.2', 485)
        cls.register('1.14.3', 490)
        cls.register('1.14.4', 498)
        cls.register('1.15', 573)
        cls.register('1.15.1', 575)
        cls.register('1.15.2', 578)
        cls.register('1.16', 735)
        cls.register('1.16.1', 736)
        cls.register('1.16.2', 751)
        cls.register('1.16.3', 753)
        cls.register('1.16.4', 754, ['1.16.5'])
        cls.register('1.17', 755)
        cls.register('1.17.1', 756)
        cls.register('1.18', 757, ['1.18.1'])
        cls.register('1.18.2', 758)
        cls.register('1.19', 759)
        cls.register('1.19.1', 760, ['1.19.2'])
        cls.register('1.19.3', 761)
        cls.register('1.19.4', 762)
        cls.register('1.20', 763, ['1.20.1'])
        cls.register('1.20.2', 764)
        cls.register('1.20.3', 765, ['1.20.4'])
        cls.register('1.20.5', 766, ['1.20.6'])
        cls.register('1.21', 767, ['1.21.1'])
        cls.register('1.21.2', 768, ['1.21.3'])
        cls.register('1.21.4', 769)


ProtocolVersion.initialize_versions()