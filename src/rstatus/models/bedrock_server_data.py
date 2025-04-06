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


@dataclass
class Players:
    online: int
    max: int


@dataclass
class BedrockServerResponse:
    ip_address: str
    port: int
    motd: MOTD
    version: Version
    players: Players
    guid: int
    gamemode: str
    brand: str
    map: str
    ping: int
    raw_response: dict