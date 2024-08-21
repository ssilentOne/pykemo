"""
Post revisions module.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .posts import Post


@dataclass(kw_only=True)
class PostRevision:
    """
    A post revision is an edit made to a post, at any given time.

    revision_id: The ID of the revision itself.
    post: The underlying post of the revision. This is a post in itself, a copy of how the
          post was at that time.
    """

    revision_id: str
    post: "Post" = field(repr=False)


    @classmethod
    def from_dict(cls, **fields) -> "PostRevision":
        """
        Initializes a PostRevision instance from a response fields.
        """

        return cls(
            revision_id=str(fields.get("revision_id")),
            post=fields.get("post")
        )
