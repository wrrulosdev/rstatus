import socket
from typing import Optional

import dns.resolver


class Resolver:
    @staticmethod
    def domain_resolver(domain: str) -> Optional[str]:
        """
        This method is used to resolve a domain to an IP address.

        :param domain: The domain to resolve.
        :return: The IP address of the domain or None if the domain could not be resolved.
        """
        try:
            return socket.gethostbyname(domain)
        
        except (socket.gaierror, OSError, UnicodeError):
            return None
        
    def minecraft_port(domain: str) -> Optional[int]:
        """
        This method is used to get the Minecraft server port from a domain.

        :param domain: The domain to get the Minecraft server port from.
        :return: The Minecraft server port or None if the port could not be found.
        """
        try:
            return dns.resolver.resolve(f'_minecraft._tcp.{domain}', 'SRV')[0].port
        
        except (dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
            return None

    @staticmethod
    def is_domain(domain: str) -> bool:
        """
        This method is used to check if a string is a domain.

        :param domain: The string to check.
        :return: True if the string is a domain, False otherwise.
        """
        try:
            socket.gethostbyname(domain)
            return True
        
        except (socket.gaierror, OSError, UnicodeError):
            return False

    @staticmethod
    def is_ip(ip: str) -> bool:
        """
        This method is used to check if a string is an IP address.

        :param ip: The string to check.
        :return: True if the string is an IP address, False otherwise.
        """
        try:
            socket.inet_aton(ip)
            return True
        
        except (socket.error, OSError):
            return False
