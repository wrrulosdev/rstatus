import re


class ClearResponse:
    @staticmethod
    def clear_response(bot_response: str) -> str:
        """
        This method is used to clear the response from the bot.

        :param str bot_response: The response from the bot.
        :return str: The cleared response.
        """
        bot_response = bot_response.replace('\n', ' ')
        bot_response = re.sub(r' +', ' ', bot_response)
        bot_response = ClearResponse.replace_mini_message_color_codes_with_minecraft_colors(bot_response)
        return bot_response
        
    @staticmethod
    def replace_mini_message_color_codes_with_minecraft_colors(message: str) -> str:
        """
        Replace MiniMessage colored characters with Minecraft color codes.
        
        :param message: Message with the mini message color codes
        :return: Message with the Minecraft color codes
        """
        codes: dict = {
            '<reset><black>': '0',
            '<reset><dark_blue>': '1',
            '<reset><dark_green>': '2',
            '<reset><dark_aqua>': '3',
            '<reset><dark_red>': '4',
            '<reset><dark_purple>': '5',
            '<reset><gold>': '6',
            '<reset><gray>': '7',
            '<reset><dark_gray>': '8',
            '<reset><blue>': '9',
            '<reset><green>': 'a',
            '<reset><aqua>': 'b',
            '<reset><red>': 'c',
            '<reset><light_purple>': 'd',
            '<reset><yellow>': 'e',
            '<reset><white>': 'f',
            '<obfuscated>': 'k',
            '<bold>': 'l',
            '<strikethrough>': 'm',
            '<underlined>': 'n',
            '<italic>': 'o',
            '<reset>': 'r',
        }

        for code in codes.items():
            message = message.replace(code[0], f'&{code[1]}').replace(code[0], f'&{code[1]}')

        message = message.replace('<newline>', '\n')
        return message