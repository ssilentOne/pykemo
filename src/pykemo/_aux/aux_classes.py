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

    file: The file itself.
    posts: All the normal posts where this file appears.
    disc: All the discord messages where this file is.
    """

    file: Optional["File"]
    posts: "PostsList"
    disc: "MessagesList"


    @classmethod
    def empty(cls) -> "FileHashResult":
        "Returns an empty instance."

        return cls(None, [], [])
