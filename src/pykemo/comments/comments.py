"""
Comments module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from .comments_rev import CommentRevision

if TYPE_CHECKING:
    from ..core import UrlLike
    from ..creators import Creator
    from ..posts import Post

DEFAULT_COMMENT_DATE_FMT: str = r"%Y-%m-%dT%H:%M:%S"
"The default date formatting to use for comments."


@dataclass(kw_only=True)
class Comment:
    """
    Comment of a post.
    Usually instantiated through :attr:`.Post.comments`

    :param id: The ID of the comment itself.
    :param parent_id: The ID of the parent comment. Used when the comment itself is a response to another.
    :param commenter_id: The ID of the author of the comment.
    :param commenter_name: The name of the author of the comment
    :param content: The actual content of the comment.
    :param published: When was the comment created.
    :param revisions: Subsequent edits of the comment.
    :param commenter: The creator of this comment.
    :param post: The parent post this comment belongs to.

    :type id: :class:`str`
    :type parent_id: Optional[:class:`str`]
    :type commenter_id: :class:`str`
    :type commenter_name: :class:`str`
    :type content: :class:`str`
    :type published: :class:`datetime.datetime`
    :type revisions: list[:class:`.CommentRevision`]
    :type commenter: :class:`.Creator`
    :type post: :class:`.Post`
    """

    id: str
    parent_id: Optional[str] = None
    commenter_id: str
    commenter_name: str
    content: str = field(repr=False)
    published: datetime = field(repr=False)
    revisions: list[CommentRevision] = field(repr=False)
    commenter: "Creator" = field(repr=False)
    post: "Post" = field(repr=False)


    @classmethod
    def from_dict(cls, **fields) -> "Comment":
        """
        Initializes a Comment instance from a response fields.

        :return: An instace of an comment.
        :rtype: :class:`.Comment`
        """

        return cls(
            id=fields.get("id"),
            parent_id=fields.get("parent_id"),
            commenter_id=fields.get("commenter"),
            commenter_name=fields.get("commenter_name"),
            content=fields.get("content", ""),
            published=datetime.strptime(fields.get("published"), DEFAULT_COMMENT_DATE_FMT),
            revisions=[CommentRevision.from_dict(**rev) for rev in fields.get("revisions")],
            commenter=fields.get("creator"),
            post=fields.get("post")
        )


    @property
    def url(self) -> "UrlLike":
        """
        :return: The direct URL of the comment.
        :rtype: :type:`.UrlLike`
        """

        return f"{self.post.url}#{self.id}"
