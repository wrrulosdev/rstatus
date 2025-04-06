# RStatus

**RStatus** is a Python library designed to query Minecraft server data, supporting both Java and Bedrock servers. It provides a unified API to retrieve server information, including server status, player counts, MOTD, version details, and more. The library also features DNS resolution and proxy support, making it easy to handle both domain names and direct IP addresses.

## Features

- **Unified API:** Retrieve data from both Java and Bedrock servers.
- **Automatic DNS Resolution:** Resolve domain names to IP addresses with custom port detection.
- **Proxy Support:** Connect via SOCKS4/5 proxies for enhanced network flexibility.
- **Bot Response:** Get the server's bot response (Java only) to retrieve additional status details.
- **Customizable Settings:** Configure timeouts, enable BungeeCord compatibility, and debug mode for troubleshooting.

## Installation

Install **RStatus** using pip:

```bash
pip install rstatus
```

> **Note:** RStatus depends on external libraries [PySocks](https://pypi.org/project/PySocks/) and [dnspython](https://pypi.org/project/dnspython/). These will be installed automatically.

## Usage

Below is a basic example of how to use **RStatus** to query a Minecraft server:

```python
from rstatus import RStatusClient

# Create a client instance for the target server (domain or IP:port)
client = RStatusClient("example.com:25565", debug=True)

# Get the server status (tries Java first, falls back to Bedrock)
server_data = client.get_server_data(bot=True)

if server_data:
    print("Server Data:", server_data)
else:
    print("Failed to retrieve server data.")
```

### Querying Specific Server Types

- **Java Server Data**

  To query data specifically from a Java server, use:

  ```python
  java_data = client.get_java_server_data(bot=True)
  
  if java_data:
      print("Java Server Data:", java_data)
  else:
      print("Java server query failed.")
  ```

- **Bedrock Server Data**

  For Bedrock servers, use:

  ```python
  bedrock_data = client.get_bedrock_server_data()
  
  if bedrock_data:
      print("Bedrock Server Data:", bedrock_data)
  else:
      print("Bedrock server query failed.")
  ```

- **Bot Response (Java Only)**

  Retrieve the bot response from a Java server with an optional version parameter:

  ```python
  bot_response = client.get_bot_response(version="1.16")
  print("Bot Response:", bot_response)
  ```

## API Reference

### `RStatusClient`

The main class provided by **RStatus** is `RStatusClient`, which inherits functionality from the underlying `MinecraftClient`, `JavaHandler`, and `BedrockHandler`.

#### Constructor

```python
RStatusClient(
    target: str,
    timeout: int = 5,
    bungeehack: bool = False,
    proxy_type: Optional[str] = None,
    proxy_address: Optional[str] = None,
    proxy_port: Optional[int] = None,
    debug: bool = False,
) -> None
```

- **`target`**: The target server address. It can be a domain (e.g., `"example.com"`) or include a port (e.g., `"example.com:25565"`).
- **`timeout`**: Connection timeout in seconds (default is 5).
- **`bungeehack`**: Enable compatibility with BungeeCord (default is `False`).
- **`proxy_type`**, **`proxy_address`**, **`proxy_port`**: Settings to connect via a proxy (supports SOCKS4/SOCKS5).
- **`debug`**: Enable debug logging for troubleshooting.

#### Methods

- **`get_server_data(bot: bool = True) -> Union[JavaServerResponse, BedrockServerResponse, None]`**  
  Retrieves the status of the server. It first attempts a Java server query and, if unsuccessful, falls back to querying a Bedrock server.

- **`get_java_server_data(bot: bool = True) -> Optional[JavaServerResponse]`**  
  Specifically queries a Java server for its status data.

- **`get_bedrock_server_data() -> Optional[BedrockServerResponse]`**  
  Queries a Bedrock server for its status data. (Note: If the port is set to 25565, it automatically switches to the default Bedrock port 19132.)

- **`get_bot_response(version: Union[str, int, None] = None) -> str`**  
  Retrieves the server’s bot response for Java servers. You can optionally specify a server version.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.