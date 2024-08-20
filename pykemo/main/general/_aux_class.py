"""
Auxiliar classes module.
"""

from typing import Optional, TYPE_CHECKING

from dataclasses import dataclass

if TYPE_CHECKING:
    from ..files import File
    from ..posts import PostsList


@dataclass(kw_only=True)
class FileHashResult:
    """
    Result used when querying for a file using its hash.
    """

    file: Optional["File"]
    posts: "PostsList"
    disc: list # to be modified later
