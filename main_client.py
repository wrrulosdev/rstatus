from typing import Optional, Union

from .utils.client import MinecraftClient
from .utils.resolver import Resolver
from .handlers import JavaHandler, BedrockHandler
from .models import JavaServerResponse, BedrockServerResponse


class RStatusClient(MinecraftClient, JavaHandler, BedrockHandler): 
    def __init__(
        self,
        target: str,
        timeout: int = 5,
        bungeehack: bool = False,
        proxy_type: Optional[str] = None,
        proxy_address: Optional[str] = None,
        proxy_port: Optional[int] = None,
        debug: bool = False,
    ) -> None:
        self.target: str = target
        self.server_address: Optional[str] = None
        self.server_port: Optional[int] = None
        self.timeout: int = timeout
        self.bungeehack: bool = bungeehack
        self.proxy_type: Optional[str] = proxy_type
        self.proxy_address: Optional[str] = proxy_address
        self.proxy_port: Optional[int] = proxy_port
        self.debug: bool = debug
        
        if ':' in self.target:
            self.target, self.server_port = self.target.split(':')
            self.server_port = int(self.server_port)
            
        if Resolver.is_domain(self.target):
            if self.server_port is None:
                self.server_port = Resolver.minecraft_port(self.target)

                if self.server_port is None:
                    self.server_port = 25565
                
            self.server_address = Resolver.domain_resolver(self.target)
            
            if self.server_address is None:
                raise ValueError(f'Could not resolve domain: {self.server_address}')

        else:
            if self.server_port is None:
                self.server_port = 25565
            
            self.server_address = self.target
            
        # Initialize MinecraftClient
        MinecraftClient.__init__(
            self,
            server_address=self.server_address,
            server_port=self.server_port,
            timeout=timeout,
            bungeehack=bungeehack,
            proxy_type=proxy_type,
            proxy_address=proxy_address,
            proxy_port=proxy_port,
            debug=debug
        )

        # Initialize JavaHandler
        JavaHandler.__init__(self, self)
        
        # Initialize BedrockHandler
        BedrockHandler.__init__(self, self)
    
    def get_server_data(self, bot: bool = True) -> Union[JavaServerResponse, BedrockServerResponse, None]:
        """
        This method is used to get the status of a server.
        
        :param bool bot: Determines if the bot connection should be used.
        :return Union[JavaServerResponse, BedrockServerResponse]: The server status data.
        """
        server_data: Optional[JavaServerResponse] = self._java_server_status(bot=bot)
        
        if server_data is None:
            server_data: Optional[BedrockServerResponse] = self.get_bedrock_server_data()
        
        return server_data

    def get_java_server_data(self, bot: bool = True) -> Optional[JavaServerResponse]:
        """
        This method is used to get the status of a Java server.
        
        :param bool bot: Determines if the bot connection should be used.
        :return Optional[JavaServerResponse]: The server status data or None if an error occurred.
        """
        return self._java_server_status(bot=bot)

    def get_bedrock_server_data(self) -> Optional[BedrockServerResponse]:
        """
        This method is used to get the status of a Bedrock server.

        :return Optional[BedrockServerResponse]: The server status data or None if an error occurred.
        """
        if self.server_port == 25565:
            self.server_port = 19132
        
        return self._bedrock_server_status()

    def get_bot_response(self, version: Union[str, int, None] = None) -> str:
        """
        This method is used to get the server response for the bot connection.
        Only works with Java servers.

        :param Union[str, int, None] version: The version of the server to get the response from.
        :return str: The server response.
        """
        return self._bot_response(version=version)