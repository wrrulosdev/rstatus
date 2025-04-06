from dataclasses import dataclass


@dataclass
class MOTD:
    text: str
    original: str


@dataclass
class Version:
    text: str
    original: str
    protocol: int
    version_name: str


@dataclass
class Players:
    online: int
    max: int
    players: str
    sample: list


@dataclass
class ModInfo:
    type: str
    mod_list: list


@dataclass
class JavaServerResponse:
    ip_address: str
    port: int
    motd: MOTD
    version: Version
    players: Players
    mod_info: ModInfo
    favicon: str
    ping: int
    bot_response: str
    brand: str
    plugin_channels: str
    raw_response: dict