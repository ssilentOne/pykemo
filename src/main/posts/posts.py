"""
Posts module.
"""

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from ..core import UrlType
from ..files import File

if TYPE_CHECKING:
    from os import PathLike

    from ..core import UrlLike
    from ..creators import Creator
    from ..services import ServiceLike


class Post:
    "Post with content."

    def __init__(self,
                 *,
                 id: str,
                 creator_id: str,
                 service: "ServiceLike",
                 title: str,
                 content: str,
                 substring: str,
                 embed: dict,
                 shared_file: bool,
                 added: datetime,
                 published: datetime,
                 edited: datetime,
                 file: File,
                 attachments: list[File],
                 creator: Optional["Creator"]=None) -> None:
        """
        Initializes a post.

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
        """

        self._id: str = id
        self._creator_id: str = creator_id
        self._service: "ServiceLike" = service
        self._title: str = title
        self._content: str = content
        self._substring: str = substring
        self._embed: dict = embed
        self._shared_file: bool = shared_file
        self._added: datetime = added
        self._published: datetime = published
        self._edited: datetime = edited
        self._file: File = file
        self._attachments: list[File] = attachments

        self._creator: Optional["Creator"] = creator


    @classmethod
    def from_dict(cls, **fields) -> "Post":
        """
        Initializes a Post instance from a response fields.
        """

        date_fmt = r"%Y-%m-%dT%H:%M:%S"

        return cls(
            id=fields.get("id"),
            creator_id=fields.get("user"),
            service=fields.get("service"),
            title=fields.get("title"),
            content=fields.get("content", ""),
            substring=fields.get("substring", ""),
            embed=fields.get("embed", {}),
            shared_file=fields.get("shared_file", False),
            added=datetime.strptime(fields.get("added"), rf"{date_fmt}.%f"),
            published=datetime.strptime(fields.get("published"), date_fmt),
            edited=datetime.strptime(fields.get("edited"), date_fmt),
            file=File.from_dict(**fields.get("file")),
            attachments=[File.from_dict(**attachment_fields)
                         for attachment_fields in fields.get("attachments")],
            creator=fields.get("creator", None)
        )


    def __str__(self) -> str:
        "Represents the Post class in a string."

        return repr(self)
    

    def __repr__(self) -> str:
        "Represents a Post as-is."

        return f"<Post '{self.title}'>"


    @property
    def id(self) -> str:
        "Gives the ID of the post."

        return self._id


    @property
    def creator_id(self) -> str:
        "Gives the ID of the creator of this post."

        return self._creator_id


    @property
    def service(self) -> "ServiceLike":
        "Gives the service of the content."

        return self._service


    @property
    def title(self) -> str:
        "Gives the title of the post."

        return self._title


    @property
    def content(self) -> str:
        "Gives the content string of the post."

        return self._content


    @property
    def substring(self) -> str:
        "Gives the sub-string of the post."

        return self._substring
    

    @property
    def embed(self) -> str:
        "Gives the embed of the post."

        return self._embed
    

    @property
    def shared_file(self) -> str:
        "Gives if the post has a shared file."

        return self._shared_file


    @property
    def added(self) -> datetime:
        "Gives when the post was added."

        return self._added


    @property
    def published(self) -> datetime:
        "Gives when the post was published."

        return self._published


    @property
    def edited(self) -> datetime:
        "Gives when the post was last edited."

        return self._edited


    @property
    def file(self) -> File:
        "Gives the file of the post preview."

        return self._file


    @property
    def attachments(self) -> list[File]:
        "Gives the files of the post."

        return self._attachments


    @property
    def creator(self) -> "Creator":
        "Gives the creator of this post."

        return self._creator


    @property
    def url(self) -> "UrlLike":
        "Gives the URL of the post."

        return f"{UrlType.SITE}/{self.service}/user/{self.creator_id}/post/{self.id}"


    @property
    def _all_files(self) -> list[File]:
        "Retrieves both the preview file and the attachments, if any."

        return [self.file] + self.attachments


    def downloaded(self) -> bool:
        """
        Checks if the entire post has all files downloaded.
        """

        for file in self._all_files:
            if not file.downloaded():
                return False

        return True


    def download(self) -> bool:
        """
        Download all the files in the post.
        Returns `True` if successful, or `False` if not.
        """

        for file in self._all_files:
            if not file.download():
                return False

        return True


    def save(self, path: Union["PathLike", Path, None]=None, force: bool=True) -> bool:
        """
        Tries to save all the files in the post.
        Returns `True` if successful, or `False` if not.

        path: The optional path where to store all the files
        force: Wether to overwrite existing files
        """

        if path is None:
            path = Path(self.title)
        elif not isinstance(path, Path):
            path = Path(path)

        path.mkdir(parents=True, exist_ok=True)
        for file in self._all_files:
            if not file.save(path, force=force):
                return False

        return True
