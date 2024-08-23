"""
Auxiliar classes module.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..discord import MessagesList
    from ..files import File
    from ..posts import PostsList


@dataclass(kw_only=True)
class FileHashResult:
    """
    Result used when querying for a file using its hash.

    :param file: The file itself.
    :param posts: All the normal posts where this file appears.
    :param disc: All the discord messages where this file is.

    :type file: :class:`.File`
    :type posts: list[:class:`.Post`]
    :type disc: list[:class:`.DiscordMessage`]
    """

    file: Optional["File"]
    posts: "PostsList"
    disc: "MessagesList"


    @classmethod
    def empty(cls) -> "FileHashResult":
        """
        :return: An instance of the result with empty fields.

        :rtype: :class:`.FileHashResult`
        """

        return cls(None, [], [])
