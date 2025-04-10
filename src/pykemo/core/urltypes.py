"""
URL types module.
"""

from typing import Any
from enum import StrEnum


class UrlType(StrEnum):
    """
    Types of URL endpoints.

    .. note:: The DATA type can be further formatted into different servers. It may not be used as-is.
    """

    SITE = "https://kemono.su"
    "The URL for the Kemono site itself."

    DATA = "https://c{i}.kemono.su"
    "The URL for the backend that stores assets."

    API = "https://kemono.su/api"
    "The URL entrypoint for the Kemono API."

    DISCORD = "https://cdn.discordapp.com"
    "A special URL specifically for Discord assets."


    def is_data(self) -> bool:
        """
        Checks if this instance is of the DATA type.
        
        :return: A boolean value describing if the instance is of the expected type or not.
        :rtype: :class:`bool`
        """

        return self == __class__.DATA


    def is_api(self) -> bool:
        """
        Checks if this instance is of the API type.
        
        :return: A boolean value describing if the instance is of the expected type or not.
        :rtype: :class:`bool`
        """

        return self == __class__.API


    def format_data(self, value: Any) -> str:
        """
        If this instance is of type DATA, then it formats the server number. If not, it simply
        returns the enum value.
        
        :param value: The value to substitue in the final string.
        
        :type value: :type:`Any`
        
        :return: The string, already formatted.
        :rtype: :class:`str`
        """

        if not self.is_data():
            return self.value

        return self.value.format(i=value)
