"""
Posts module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional, TypeAlias, Union

from tqdm import tqdm

from ..comments import Comment
from ..core import UrlType, get
from ..files import BAR_WIDTH, File
from .post_revisions import PostRevision

if TYPE_CHECKING:
    from os import PathLike

    from ..core import UrlLike
    from ..creators import Creator
    from ..services import ServiceLike

PostsList: TypeAlias = list["Post"]
DateOrFmt: TypeAlias = Union[str, datetime]
CommentsList: TypeAlias = list[Comment]
PostRevsList: TypeAlias = list[PostRevision]

ELEMENTS_PER_PAGE: int = 50
"""
This is how the API ortganizes the posts and other things.
Each 'page' has fifty (50) elements at most.
"""

DEFAULT_DATE_FMT: str = r"%Y-%m-%dT%H:%M:%S"
"The default date formatting to use."


@dataclass(kw_only=True)
class Post:
    """
    Post with content.

    id: The ID of the post.
    creator_id: The creator's ID that owns the post content (not the user that uploaded it).
    service: The services that provides the content.
    title: The title of the post.
    content: The content string of the post.
    substring: The sub-string for the post description.
    embed: A dictionary denoting the embed.
    shared_file: Wether the post has a shared file.
    added: When was the post added.
    published: When was the post published.
    edited: When was the post last edited.
    file: The file that the posts uses when previewed.
    attachments: All the files under this post.
    comments: The comments of this post. May be unloaded.
    """

    id: str
    creator_id: str
    service: "ServiceLike"
    title: str
    content: str = field(repr=False)
    substring: str = field(repr=False)
    embed: dict = field(repr=False)
    shared_file: bool = field(repr=False)
    added: Optional[datetime] = field(default=None, repr=False)
    published: datetime = field(repr=False)
    edited: Optional[datetime] = field(default=None, repr=False)
    file: Optional[File] = field(default=None, repr=False)
    attachments: list[File] = field(repr=False)
    creator: "Creator" = field(repr=False)
    is_revision: bool = field(default=False, repr=False)

    # unloaded fields
    _comments: CommentsList = field(default_factory=list, init=False, repr=False)
    __comm_loaded: bool = field(default=False, init=False, repr=False)

    _flagged: bool = field(default=False, init=False, repr=False)
    __flag_loaded: bool = field(default=False, init=False, repr=False)

    _revisions: PostRevsList = field(default_factory=list, init=False, repr=False)
    __revs_loaded: bool = field(default=False, init=False, repr=False)


    @classmethod
    def from_dict(cls, **fields) -> "Post":
        """
        Initializes a Post instance from a response fields.
        """

        added_field = fields.get("added", None)
        added = (cls.str_to_date(added_field, rf"{DEFAULT_DATE_FMT}.%f")
                 if added_field is not None
                 else None)
        
        edited_field = fields.get("edited", None)
        edited = (cls.str_to_date(edited_field, DEFAULT_DATE_FMT)
                 if edited_field is not None
                 else None)
        
        file_dict = fields.get("file")

        return cls(
            id=fields.get("id"),
            creator_id=fields.get("user"),
            service=fields.get("service"),
            title=fields.get("title"),
            content=fields.get("content", ""),
            substring=fields.get("substring", ""),
            embed=fields.get("embed", {}),
            shared_file=fields.get("shared_file", False),
            added=added,
            published=cls.str_to_date(fields.get("published"), DEFAULT_DATE_FMT),
            edited=edited,
            file=(File.from_dict(**file_dict) if file_dict else None),
            attachments=[File.from_dict(**attachment_fields)
                         for attachment_fields in fields.get("attachments")],
            creator=fields.get("creator", None),
            is_revision=fields.get("is_revision", False)
        )


    @property
    def comments(self) -> CommentsList:
        "Loads the comments of the post."

        if not self.__comm_loaded:
            self.__comm_loaded = True
            self._comments = self.fetch_comments()

        return self._comments

    @property
    def flagged(self) -> bool:
        "Checks if the post is flagged for reimport."

        if not self.__flag_loaded and not self.is_revision:
            self.__flag_loaded = True
            self._flagged = self._fetch_flagged()

        return self._flagged


    @property
    def revisions(self) -> PostRevsList:
        "Retrieves all the revisions of this post."

        if not self.__revs_loaded and not self.is_revision:
            self.__revs_loaded = True
            self._revisions = self._fetch_revisions()

        return self._revisions


    @property
    def url(self) -> "UrlLike":
        "Gives the URL of the post."

        return f"{UrlType.SITE}/{self.service}/user/{self.creator_id}/post/{self.id}"


    @property
    def _all_files(self) -> list[File]:
        "Retrieves both the preview file and the attachments, if any."

        return ([self.file] if self.file is not None else []) + self.attachments


    @staticmethod
    def str_to_date(date: str, fmt: str=DEFAULT_DATE_FMT) -> datetime:
        "Converts a date with a given format to a datetime object."

        return datetime.strptime(date, fmt)


    @staticmethod
    def _process_fmt(fmt: Optional[str], /) -> str:
        "Converts the format to a default one if it is not present."

        return (fmt if fmt is not None else DEFAULT_DATE_FMT)


    @staticmethod
    def _process_date(date: DateOrFmt, fmt: Optional[str]) -> datetime:
        "Process the date if it is a string, or uses as-is if it is already a datetime object."

        if isinstance(date, str):
            return Post.str_to_date(date, Post._process_fmt(fmt))

        return date


    @staticmethod
    def before_static(date1: DateOrFmt,
                      date2: DateOrFmt,
                      *,
                      fmt1: Optional[str]=None,
                      fmt2: Optional[str]=None) -> bool:
        "Compares if the dates (in string form) with date1 < date2"

        return Post._process_date(date1, fmt1) < Post._process_date(date2, fmt2)


    def before(self, date: datetime) -> bool:
        "Verifies if the post was published before a certain date."

        return self.published < date


    @staticmethod
    def since_static(date1: DateOrFmt,
                     date2: DateOrFmt,
                     *,
                     fmt1: Optional[str]=None,
                     fmt2: Optional[str]=None) -> bool:
        "Compares if the dates (in string form) with date1 >= date2"

        return Post._process_date(date1, fmt1) >= Post._process_date(date2, fmt2)


    def since(self, date: datetime) -> bool:
        "Verifies if the post was published after a certain date."

        return self.published >= date


    def save(self,
             path: Union["PathLike", Path, None]=None,
             force: bool=True,
             verbose: bool=True) -> bool:
        """
        Tries to save all the files in the post.
        Returns `True` if successful, or `False` if not.

        path: The optional path where to store all the files. If it ends with '/*', it will
              use its default name inside such folder.
        force: Wether to overwrite existing files
        verbose: Wether to track progress.
        """

        files = self._all_files
        if verbose:
            if not files:
                print(f"Post '{self.title}' doesn't have files to download. Ignoring...")
                return False

            files = tqdm(files,
                         desc=f"Post '{self.title}'",
                         ncols=BAR_WIDTH,
                         unit="file",
                         position=0,
                         smoothing=1.0,
                         colour="blue")

        if path is None:
            path = Path(self.title)
        elif isinstance(path, str) and path.endswith("/*"):
            path = Path(f"{path[:-1]}{self.title}")
        elif not isinstance(path, Path):
            path = Path(path)

        path.mkdir(parents=True, exist_ok=True)

        for file in files:
            if not file.save(path, force=force, verbose=verbose):
                return False

        return True


    def fetch_comments(self) -> CommentsList:
        """
        Fetches the comments of the post. This is designed for internal purposes, as it is
        recommended to use the `comments` property instead.
        However, it can also be used as-is to prevent using a potentially outdated field.
        """

        response = get(f"/{self.service}/user/{self.creator_id}/post/{self.id}/comments")
        comments = []

        for comment_fields in response.json():
            comment_fields.update(creator=self.creator, post=self)
            comments.append(Comment.from_dict(**comment_fields))

        return comments

    def _fetch_flagged(self) -> bool:
        """
        Checks with a request if a post is flagged for reimport.
        According to the docs, it should have status code of 200 if it is flagged, and
        404 if it's not.
        """

        response = get(f"/{self.service}/user/{self.creator_id}/post/{self.id}/flag")
        return response.status_code == 200


    def _fetch_revisions(self) -> PostRevsList:
        """
        Fetches a request all the revisions of the post.
        """

        response = get(f"/{self.service}/user/{self.creator_id}/post/{self.id}/revisions")
        revisions = []

        for revs_fields in response.json():
            revs_fields.update(creator=self.creator, is_revision=True)
            subpost = Post.from_dict(**revs_fields)

            revs_fields.update(post=subpost)
            revisions.append(PostRevision.from_dict(**revs_fields))

        return revisions
