class BotResponse:
    BUNGEEHACK: str = '&dVulnerable to BungeeHack'
    IP_FORWARDING: str = '&dIP Forwarding detected (Possibly vulnerable)'
    IPWHITELIST: str = '&cIPWhitelist'
    BUNGEEGUARD: str = '&cBungeeGuard'
    PROTECTED: str = '&cProtected'
    FORGE: str = '&bForge'
    ANTI_VPN: str = '&cAnti-VPN'
    PREMIUM: str = '&6&lServer in premium mode'
    AUTHSERVERS_DOWN: str = '&6The authentication servers are down (Mojang).'
    INCOMPATIBLE: str = '&cIncompatible server version'
    BANNED: str = '&cYou are banned from this server.'
    WHITELIST: str = '&bYou are not whitelisted on this server.'
    CONNECTED: str = '&a&lConnected'

    @staticmethod
    def custom_response(bot_response: str) -> str:
        """
        This method is used to clear the response from the bot.

        :param str bot_response: The response from the bot.
        :return str: The cleared response.
        """
        if 'If you wish to use IP forwarding, please enable it in your BungeeCord config as well!' in bot_response:
            return BotResponse.IP_FORWARDING
        
        if 'You have to join through' in bot_response:
            return BotResponse.IPWHITELIST
        
        if 'Unable to authenticate' in bot_response:
            return BotResponse.BUNGEEGUARD
        
        if 'Please join to the server via' in bot_response:
            return BotResponse.PROTECTED
        
        if 'FML/Forge' in bot_response or 'has mods that require Forge' in bot_response:
            return BotResponse.FORGE
        
        if 'VPN' in bot_response:
            return BotResponse.ANTI_VPN
        
        # Minecraft default messages
        if 'multiplayer.disconnect.invalid_public_key_signature' in bot_response:
            return BotResponse.PREMIUM
        
        if 'multiplayer.disconnect.authservers_down' in bot_response:
            return BotResponse.AUTHSERVERS_DOWN
        
        if 'multiplayer.disconnect.incompatible' in bot_response:
            return BotResponse.INCOMPATIBLE
        
        if 'multiplayer.disconnect.not_whitelisted' in bot_response or 'You are not whitelisted on this server!' in bot_response:
            return BotResponse.WHITELIST
        
        if 'multiplayer.disconnect.banned.reasonwith' in bot_response:
            return BotResponse.BANNED
        
        # RStatus bot response messages
        if bot_response == 'The server is in online mode':
            return BotResponse.PREMIUM
        
        if bot_response == 'Connected':
            return BotResponse.CONNECTED
        
        if bot_response == 'Connected with BungeeHack':
            return BotResponse.BUNGEEHACK
        
        return bot_response
