"""
Comment revisions module.
"""

from dataclasses import dataclass
from datetime import datetime

DEFAULT_REV_DATE_FMT: str = r"%Y-%m-%dT%H:%M:%S.%f"
"The default date formatting to use for comment revisions."


@dataclass(kw_only=True)
class CommentRevision:
    """
    A comment revision.
    A revision is an edit that can be applied to any given comment by its author, provided that
    they wanted to changes its contents at some point.

    id: The ID of the revision. Usually an integer indicating the number of the revision.
    content: The modified contents of the message.
    added: When was this revision applied.
    """

    id: int
    content: str
    added: datetime


    @classmethod
    def from_dict(cls, **fields) -> "CommentRevision":
        """
        Initializes a CommentRevision instance from a response fields.
        """

        return cls(
            id=fields.get("id"),
            content=fields.get("content", ""),
            added=datetime.strptime(fields.get("added"), DEFAULT_REV_DATE_FMT)
        )
